<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\PokerTournament;
use App\Models\PokerTournamentEntry;
use App\Models\PokerWallet;
use App\Events\PokerLobbyUpdate;
use App\Events\PokerTournamentUpdate;
use Illuminate\Http\Request;

class PokerTournamentController extends Controller
{
    // 토너먼트 목록 (예정 + 진행중)
    public function index()
    {
        $upcoming = PokerTournament::upcoming()
            ->withCount(['entries as registered_count', 'entries as online_count' => function ($q) {
                $q->where('is_online', true);
            }])
            ->get();

        $running = PokerTournament::running()
            ->withCount(['entries as registered_count', 'entries as online_count' => function ($q) {
                $q->where('is_online', true);
            }, 'entries as remaining_count' => function ($q) {
                $q->whereIn('status', ['seated', 'playing']);
            }])
            ->get();

        return response()->json([
            'success' => true,
            'data' => [
                'upcoming' => $upcoming,
                'running' => $running,
            ],
        ]);
    }

    // 토너먼트 상세 + 대기실 명단
    public function show($id)
    {
        $tournament = PokerTournament::withCount(['entries as registered_count', 'entries as online_count' => function ($q) {
            $q->where('is_online', true);
        }])->findOrFail($id);

        $entries = PokerTournamentEntry::where('tournament_id', $id)
            ->with('user:id,name,nickname,avatar')
            ->orderByDesc('is_online')
            ->orderBy('created_at')
            ->get()
            ->map(fn($e) => [
                'id' => $e->id,
                'user_id' => $e->user_id,
                'user_name' => $e->user->nickname ?? $e->user->name ?? '?',
                'avatar' => $e->user->avatar,
                'status' => $e->status,
                'is_online' => $e->is_online,
                'chips' => $e->chips,
                'finish_position' => $e->finish_position,
                'registered_at' => $e->created_at->format('H:i'),
            ]);

        return response()->json([
            'success' => true,
            'data' => [
                'tournament' => $tournament,
                'entries' => $entries,
            ],
        ]);
    }

    // 토너먼트 참가 신청
    public function register(Request $request, $id)
    {
        $user = $request->user();
        $tournament = PokerTournament::findOrFail($id);

        if (!in_array($tournament->status, ['scheduled', 'registering'])) {
            return response()->json(['success' => false, 'message' => '참가 신청이 마감되었습니다.'], 422);
        }

        if ($tournament->entries()->count() >= $tournament->max_players) {
            return response()->json(['success' => false, 'message' => '정원이 초과되었습니다.'], 422);
        }

        // 이미 참가 중인지 체크
        if ($tournament->entries()->where('user_id', $user->id)->exists()) {
            return response()->json(['success' => false, 'message' => '이미 참가 신청되어 있습니다.'], 422);
        }

        // 바이인 차감 (프리롤 제외)
        if ($tournament->buy_in > 0) {
            $wallet = PokerWallet::where('user_id', $user->id)->first();
            if (!$wallet || $wallet->chips_balance < $tournament->buy_in) {
                return response()->json(['success' => false, 'message' => "칩이 부족합니다. (필요: {$tournament->buy_in})"], 422);
            }
            $wallet->withdraw($tournament->buy_in, "토너먼트 참가: {$tournament->title}");
        }

        $entry = PokerTournamentEntry::create([
            'tournament_id' => $id,
            'user_id' => $user->id,
            'status' => 'registered',
            'is_online' => true,
            'last_seen_at' => now(),
            'chips' => $tournament->starting_chips,
        ]);

        // 실시간 알림
        broadcast(new PokerTournamentUpdate($tournament->fresh()->loadCount([
            'entries as registered_count',
            'entries as online_count' => fn($q) => $q->where('is_online', true),
        ])))->toOthers();

        return response()->json([
            'success' => true,
            'data' => $entry,
            'message' => '참가 신청 완료!',
        ]);
    }

    // 참가 취소
    public function unregister(Request $request, $id)
    {
        $user = $request->user();
        $entry = PokerTournamentEntry::where('tournament_id', $id)
            ->where('user_id', $user->id)
            ->where('status', 'registered')
            ->first();

        if (!$entry) {
            return response()->json(['success' => false, 'message' => '참가 신청을 찾을 수 없습니다.'], 404);
        }

        $tournament = PokerTournament::findOrFail($id);

        // 바이인 환불
        if ($tournament->buy_in > 0) {
            $wallet = PokerWallet::firstOrCreate(
                ['user_id' => $user->id],
                ['chips_balance' => 0, 'total_deposited' => 0, 'total_withdrawn' => 0]
            );
            $wallet->deposit($tournament->buy_in, "토너먼트 취소 환불: {$tournament->title}");
        }

        $entry->delete();

        broadcast(new PokerTournamentUpdate($tournament->fresh()->loadCount([
            'entries as registered_count',
            'entries as online_count' => fn($q) => $q->where('is_online', true),
        ])))->toOthers();

        return response()->json(['success' => true, 'message' => '참가가 취소되었습니다.']);
    }

    // 온라인 상태 업데이트 (heartbeat)
    public function heartbeat(Request $request, $id)
    {
        $entry = PokerTournamentEntry::where('tournament_id', $id)
            ->where('user_id', $request->user()->id)
            ->first();

        if ($entry) {
            $entry->update(['is_online' => true, 'last_seen_at' => now()]);
        }

        return response()->json(['success' => true]);
    }

    // ─── Admin: 토너먼트 생성 (일회성 or 반복 스케줄 템플릿) ───
    public function adminCreate(Request $request)
    {
        $isSchedule = $request->boolean('is_schedule');

        if ($isSchedule) {
            // 반복 스케줄 템플릿 생성
            $request->validate([
                'title' => 'required|string|max:100',
                'type' => 'in:freeroll,micro,regular,high_roller',
                'buy_in' => 'required|integer|min:0',
                'starting_chips' => 'required|integer|min:1000',
                'max_players' => 'required|integer|min:9|max:1000',
                'schedule_time' => 'required|string', // "18:00"
                'schedule_days' => 'required|array', // ["mon","tue",...]
            ]);

            $template = PokerTournament::create([
                'title' => $request->title,
                'type' => $request->type ?? 'regular',
                'status' => 'scheduled',
                'buy_in' => $request->buy_in,
                'starting_chips' => $request->starting_chips,
                'max_players' => $request->max_players,
                'min_players' => $request->min_players ?? 9,
                'scheduled_at' => now()->addDay()->format('Y-m-d') . ' ' . $request->schedule_time,
                'registration_opens_at' => now(),
                'late_reg_levels' => $request->late_reg_levels ?? 3,
                'bounty_pct' => $request->bounty_pct ?? 10,
                'is_template' => true,
                'schedule_pattern' => [
                    'recurring' => true,
                    'days' => $request->schedule_days,
                    'time' => $request->schedule_time,
                ],
            ]);

            // 즉시 오늘/내일 토너먼트도 생성
            \Artisan::call('poker:generate-tournaments');

            return response()->json(['success' => true, 'data' => $template, 'message' => '반복 스케줄이 등록되었습니다. 매일 자동 생성됩니다.']);
        }

        // 일회성 토너먼트 생성
        $request->validate([
            'title' => 'required|string|max:100',
            'type' => 'in:freeroll,micro,regular,high_roller',
            'buy_in' => 'required|integer|min:0',
            'starting_chips' => 'required|integer|min:1000',
            'max_players' => 'required|integer|min:9|max:1000',
            'min_players' => 'integer|min:2',
            'scheduled_at' => 'required|date',
        ]);

        $tournament = PokerTournament::create([
            'title' => $request->title,
            'type' => $request->type ?? 'regular',
            'status' => 'scheduled',
            'buy_in' => $request->buy_in,
            'starting_chips' => $request->starting_chips,
            'max_players' => $request->max_players,
            'min_players' => $request->min_players ?? 9,
            'scheduled_at' => $request->scheduled_at,
            'registration_opens_at' => $request->registration_opens_at ?? now(),
            'late_reg_levels' => $request->late_reg_levels ?? 3,
            'bounty_pct' => $request->bounty_pct ?? 10,
        ]);

        broadcast(new PokerLobbyUpdate())->toOthers();

        return response()->json(['success' => true, 'data' => $tournament, 'message' => '토너먼트가 생성되었습니다.']);
    }

    // Admin: 토너먼트 목록
    public function adminList()
    {
        $tournaments = PokerTournament::withCount('entries')
            ->orderByDesc('scheduled_at')
            ->paginate(20);

        return response()->json(['success' => true, 'data' => $tournaments]);
    }

    // Admin: 토너먼트 취소
    public function adminCancel($id)
    {
        $tournament = PokerTournament::findOrFail($id);
        if ($tournament->status === 'running') {
            return response()->json(['success' => false, 'message' => '진행 중인 토너먼트는 취소할 수 없습니다.'], 422);
        }

        // 참가자 전원 환불
        foreach ($tournament->entries as $entry) {
            if ($tournament->buy_in > 0) {
                $wallet = PokerWallet::firstOrCreate(
                    ['user_id' => $entry->user_id],
                    ['chips_balance' => 0, 'total_deposited' => 0, 'total_withdrawn' => 0]
                );
                $wallet->deposit($tournament->buy_in, "토너먼트 취소 환불: {$tournament->title}");
            }
        }

        $tournament->update(['status' => 'cancelled']);
        $tournament->entries()->delete();

        return response()->json(['success' => true, 'message' => '토너먼트가 취소되었습니다.']);
    }
}
