<?php

namespace App\Http\Controllers\API;

use App\Events\PokerAction;
use App\Events\PokerChat;
use App\Http\Controllers\Controller;
use App\Models\PokerGame;
use App\Models\PokerTournament;
use App\Services\PokerGameEngine;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;

class PokerMultiController extends Controller
{
    // ── 토너먼트 참가 ──
    public function joinTournament(Request $request, $tournamentId)
    {
        $tournament = PokerTournament::findOrFail($tournamentId);
        $user = auth()->user();

        // 이미 참가 확인
        $existing = \DB::table('poker_tournament_entries')
            ->where('tournament_id', $tournamentId)
            ->where('user_id', $user->id)
            ->first();
        if ($existing) return response()->json(['success' => false, 'message' => '이미 참가 중입니다.'], 422);

        // 바이인 포인트 확인
        $wallet = $user->pokerWallet;
        if (!$wallet || $wallet->chips_balance < $tournament->buy_in) {
            return response()->json(['success' => false, 'message' => "칩 부족. 필요: {$tournament->buy_in}, 보유: " . ($wallet->chips_balance ?? 0)], 422);
        }

        // 칩 차감 + 엔트리 생성
        $wallet->decrement('chips_balance', $tournament->buy_in);
        \DB::table('poker_tournament_entries')->insert([
            'tournament_id' => $tournamentId,
            'user_id' => $user->id,
            'status' => 'registered',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $entryCount = \DB::table('poker_tournament_entries')
            ->where('tournament_id', $tournamentId)
            ->where('status', 'registered')
            ->count();

        return response()->json([
            'success' => true,
            'message' => '토너먼트 참가 완료!',
            'entry_count' => $entryCount,
        ]);
    }

    // ── 대기실 상태 ──
    public function waitingRoom($tournamentId)
    {
        $tournament = PokerTournament::findOrFail($tournamentId);
        $entries = \DB::table('poker_tournament_entries')
            ->where('tournament_id', $tournamentId)
            ->where('status', 'registered')
            ->join('users', 'users.id', '=', 'poker_tournament_entries.user_id')
            ->select('users.id', 'users.name', 'users.nickname', 'users.avatar')
            ->get();

        return response()->json([
            'success' => true,
            'data' => [
                'tournament' => $tournament,
                'players' => $entries,
                'count' => $entries->count(),
                'min_players' => $tournament->min_players ?? 2,
                'max_players' => $tournament->max_players ?? 9,
                'can_start' => $entries->count() >= ($tournament->min_players ?? 2),
            ],
        ]);
    }

    // ── 캐시 게임 (빠른 매칭) ──
    public function quickMatch(Request $request)
    {
        $user = auth()->user();
        $gameType = $request->type ?? 'normal'; // normal(15초) or speed(10초)
        $turnTime = $gameType === 'speed' ? 10 : 15;
        $bb = $request->bb ?? 20;

        // 대기열에 추가
        $queueKey = "poker_queue_{$gameType}_{$bb}";
        $queue = Cache::get($queueKey, []);

        // 이미 대기 중인지 확인
        if (collect($queue)->where('id', $user->id)->count()) {
            return response()->json(['success' => true, 'message' => '매칭 대기 중...', 'status' => 'waiting']);
        }

        $queue[] = [
            'id' => $user->id,
            'name' => $user->nickname ?? $user->name,
            'chips' => $user->pokerWallet?->chips_balance ?? 15000,
            'joinedAt' => time(),
        ];

        Cache::put($queueKey, $queue, 300); // 5분 TTL

        // 30초 대기 후 AI로 채워서 시작 (또는 2명 이상이면 즉시)
        $waitTime = 30;
        $firstJoin = collect($queue)->min('joinedAt') ?? time();
        $waited = time() - $firstJoin;
        $shouldStart = count($queue) >= 2 || $waited >= $waitTime;

        if ($shouldStart) {
            $players = array_slice($queue, 0, min(count($queue), 9));

            // AI로 빈 자리 채우기 (최소 2명 테이블)
            $aiNames = [
                ['name' => '대니얼', 'style' => 'TAG'], ['name' => '소피아', 'style' => 'LAG'],
                ['name' => '재민', 'style' => 'TP'], ['name' => '린다', 'style' => 'LP'],
                ['name' => '마이크', 'style' => 'maniac'], ['name' => '유나', 'style' => 'balanced'],
                ['name' => '빅터', 'style' => 'nit'], ['name' => '하나', 'style' => 'tricky'],
            ];
            shuffle($aiNames);
            $aiIdx = 0;
            $targetCount = max(count($players) + 1, 4); // 최소 4명 테이블
            while (count($players) < $targetCount && $aiIdx < count($aiNames)) {
                $ai = $aiNames[$aiIdx++];
                $players[] = ['id' => -$aiIdx, 'name' => $ai['name'] . ' (AI)', 'chips' => 15000, 'isAI' => true, 'style' => $ai['style']];
            }
            Cache::forget($queueKey);

            $state = PokerGameEngine::createGame($players, [
                'bb' => $bb,
                'sb' => intdiv($bb, 2),
                'turnTime' => $turnTime,
                'type' => $gameType,
            ]);

            // DB 기록
            PokerGame::create([
                'game_id' => $state['gameId'],
                'type' => 'cash',
                'status' => 'playing',
                'config' => json_encode($state['config']),
                'player_count' => count($players),
            ]);

            // 각 플레이어에게 브로드캐스트
            foreach ($players as $p) {
                $view = PokerGameEngine::getPlayerView($state, $p['id']);
                broadcast(new PokerAction($state['gameId'], $view, ['type' => 'game_start']))->toOthers();
            }

            return response()->json([
                'success' => true,
                'message' => '게임 시작!',
                'status' => 'started',
                'gameId' => $state['gameId'],
                'state' => PokerGameEngine::getPlayerView($state, $user->id),
            ]);
        }

        return response()->json([
            'success' => true,
            'message' => '매칭 대기 중... (' . count($queue) . '명)',
            'status' => 'waiting',
            'queue_count' => count($queue),
        ]);
    }

    // ── 게임 상태 조회 ──
    public function getState($gameId)
    {
        $state = PokerGameEngine::getGameState($gameId);
        if (!$state) return response()->json(['success' => false, 'message' => '게임을 찾을 수 없습니다.'], 404);

        return response()->json([
            'success' => true,
            'data' => PokerGameEngine::getPlayerView($state, auth()->id()),
        ]);
    }

    // ── 플레이어 액션 ──
    public function action(Request $request, $gameId)
    {
        $request->validate([
            'action' => 'required|in:fold,check,call,raise,allin',
            'amount' => 'nullable|integer|min:0',
        ]);

        $result = PokerGameEngine::processAction($gameId, auth()->id(), $request->action, $request->amount ?? 0);

        if (isset($result['error'])) {
            return response()->json(['success' => false, 'message' => $result['error']], 422);
        }

        // 모든 플레이어에게 업데이트 브로드캐스트
        // 각 플레이어는 자기 카드만 볼 수 있게 개별 전송
        foreach ($result['seats'] as $seat) {
            if (isset($seat['id']) && $seat['id'] > 0) {
                $view = PokerGameEngine::getPlayerView($result, $seat['id']);
                // 개별 유저 채널로 전송
                broadcast(new PokerAction($gameId, $view, $result['lastAction']))->toOthers();
            }
        }

        return response()->json([
            'success' => true,
            'data' => PokerGameEngine::getPlayerView($result, auth()->id()),
        ]);
    }

    // ── 인게임 채팅 ──
    public function chat(Request $request, $gameId)
    {
        $request->validate(['message' => 'required|max:200']);
        $user = auth()->user();

        broadcast(new PokerChat($gameId, $user->id, $user->nickname ?? $user->name, $request->message));

        return response()->json(['success' => true]);
    }

    // ── 타임아웃 체크 (cron으로 매초 실행 or 클라이언트 폴링) ──
    public function checkTimeout($gameId)
    {
        $state = PokerGameEngine::getGameState($gameId);
        if (!$state || $state['status'] !== 'playing') {
            return response()->json(['success' => true, 'timeout' => false]);
        }

        $actIdx = $state['actIdx'];
        $seat = $state['seats'][$actIdx] ?? null;

        // AI 턴이면 서버에서 자동 처리
        if ($seat && $seat['id'] < 0) {
            $result = PokerGameEngine::processAITurn($gameId);
            if ($result && !isset($result['error'])) {
                // AI 처리 후 다음도 AI면 연속 처리 (최대 8번)
                for ($i = 0; $i < 8; $i++) {
                    $nextState = PokerGameEngine::getGameState($gameId);
                    if (!$nextState || $nextState['status'] !== 'playing') break;
                    $nextSeat = $nextState['seats'][$nextState['actIdx']] ?? null;
                    if (!$nextSeat || $nextSeat['id'] > 0) break; // 실제 유저 턴
                    usleep(500000); // 0.5초 딜레이
                    PokerGameEngine::processAITurn($gameId);
                }

                $finalState = PokerGameEngine::getGameState($gameId);
                return response()->json([
                    'success' => true,
                    'timeout' => false,
                    'ai_acted' => true,
                    'state' => $finalState ? PokerGameEngine::getPlayerView($finalState, auth()->id()) : null,
                    'remaining' => ($finalState['turnDeadline'] ?? time()) - time(),
                ]);
            }
        }

        // 유저 타임아웃
        if (time() > $state['turnDeadline'] && $seat && $seat['id'] > 0) {
            $toCall = max(0, $state['betLevel'] - $seat['bet']);
            $action = $toCall === 0 ? 'check' : 'fold';
            $result = PokerGameEngine::processAction($gameId, $seat['id'], $action);
            return response()->json(['success' => true, 'timeout' => true, 'action' => $action]);
        }

        return response()->json(['success' => true, 'timeout' => false, 'remaining' => max(0, $state['turnDeadline'] - time())]);
    }
}
