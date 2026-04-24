<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\GameRecord;
use Illuminate\Http\Request;

class GameRecordController extends Controller
{
    // 레벨업 포인트 / 신기록 포인트 — 한 곳에서 관리
    private const LEVEL_UP_POINTS = 3;
    private const NEW_RECORD_POINTS = 10;

    /**
     * 게임 결과 기록
     * POST /api/games/result
     * body: { game_slug, level, time_ms, score?, won? , leveled_up? }
     * - won=true 이고 leveled_up=true 면: 레벨업 +3P
     * - 신기록 달성 시: +10P
     * returns: { success, data: { leveled_up, new_record, points_earned, prev_time_ms, rank } }
     */
    public function store(Request $request)
    {
        $data = $request->validate([
            'game_slug'   => 'required|string|max:50',
            'level'       => 'required|integer|min:1|max:10',
            'time_ms'     => 'required|integer|min:1',
            'score'       => 'nullable|integer|min:0',
            'won'         => 'nullable|boolean',
            'leveled_up'  => 'nullable|boolean',
        ]);

        $user = auth()->user();
        $slug = $data['game_slug'];
        $level = (int) $data['level'];
        $timeMs = (int) $data['time_ms'];
        $score = (int) ($data['score'] ?? 0);
        $won = (bool) ($data['won'] ?? false);
        $leveledUp = (bool) ($data['leveled_up'] ?? false);

        $pointsEarned = 0;
        $newRecord = false;
        $prevTimeMs = null;

        // 1) 레벨업 포인트 — 이긴 경우에만
        if ($won && $leveledUp) {
            $user->addPoints(self::LEVEL_UP_POINTS, "게임 레벨업 ($slug Lv.$level)", 'earn', [
                'type' => GameRecord::class,
                'id'   => null,
            ]);
            $pointsEarned += self::LEVEL_UP_POINTS;
        }

        // 2) 신기록 — 이긴 경우에만 + time_ms 가 기존보다 작을 때
        if ($won) {
            $existing = GameRecord::where('user_id', $user->id)
                ->where('game_slug', $slug)
                ->where('level', $level)
                ->first();

            if (!$existing) {
                GameRecord::create([
                    'user_id'   => $user->id,
                    'game_slug' => $slug,
                    'level'     => $level,
                    'time_ms'   => $timeMs,
                    'score'     => $score,
                ]);
                $newRecord = true;
            } elseif ($timeMs < $existing->time_ms) {
                $prevTimeMs = $existing->time_ms;
                $existing->update(['time_ms' => $timeMs, 'score' => max($existing->score, $score)]);
                $newRecord = true;
            }

            if ($newRecord) {
                $user->addPoints(self::NEW_RECORD_POINTS, "게임 신기록 ($slug Lv.$level)", 'earn');
                $pointsEarned += self::NEW_RECORD_POINTS;
            }
        }

        // 3) 현재 유저 랭킹 (게임+레벨)
        $rank = null;
        $my = GameRecord::where('user_id', $user->id)
            ->where('game_slug', $slug)
            ->where('level', $level)
            ->first();
        if ($my) {
            $rank = GameRecord::where('game_slug', $slug)
                ->where('level', $level)
                ->where('time_ms', '<', $my->time_ms)
                ->count() + 1;
        }

        return response()->json([
            'success' => true,
            'data'    => [
                'leveled_up'    => $leveledUp,
                'new_record'    => $newRecord,
                'prev_time_ms'  => $prevTimeMs,
                'points_earned' => $pointsEarned,
                'rank'          => $rank,
                'balance'       => $user->fresh()->points,
            ],
        ]);
    }

    /**
     * 리더보드 (게임 + 레벨 별 상위 10명)
     * GET /api/games/{slug}/leaderboard?level=X
     */
    public function leaderboard(Request $request, string $slug)
    {
        $level = (int) $request->input('level', 1);

        $records = GameRecord::with('user:id,name,nickname,avatar')
            ->where('game_slug', $slug)
            ->where('level', $level)
            ->orderBy('time_ms', 'asc')
            ->limit(10)
            ->get()
            ->map(function ($r, $i) {
                return [
                    'rank'     => $i + 1,
                    'user_id'  => $r->user_id,
                    'name'     => $r->user?->nickname ?? $r->user?->name ?? '알 수 없음',
                    'avatar'   => $r->user?->avatar,
                    'time_ms'  => $r->time_ms,
                    'score'    => $r->score,
                    'set_at'   => $r->updated_at?->format('Y-m-d'),
                ];
            });

        // 내 기록 (상위 10위 밖이어도 같이 반환)
        $myRank = null;
        $myRecord = null;
        if (auth()->check()) {
            $my = GameRecord::where('user_id', auth()->id())
                ->where('game_slug', $slug)
                ->where('level', $level)
                ->first();
            if ($my) {
                $myRank = GameRecord::where('game_slug', $slug)
                    ->where('level', $level)
                    ->where('time_ms', '<', $my->time_ms)
                    ->count() + 1;
                $myRecord = [
                    'rank'    => $myRank,
                    'time_ms' => $my->time_ms,
                    'score'   => $my->score,
                ];
            }
        }

        return response()->json([
            'success' => true,
            'data'    => $records,
            'my'      => $myRecord,
        ]);
    }
}
