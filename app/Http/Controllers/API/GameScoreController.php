<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;

class GameScoreController extends Controller
{
    // POST /api/games/{id}/score — 게임 점수 저장
    public function saveScore(Request $req, $gameId)
    {
        $user = Auth::user();
        $score    = (int) $req->input('score', 0);
        $duration = (int) $req->input('duration', 0);
        $result   = $req->input('result', 'win'); // win/lose/draw
        $level    = (int) $req->input('level', 1);

        // 게임 정보 조회
        $game = DB::table('games')->where('id', $gameId)->first();
        if (!$game) {
            return response()->json(['error' => '게임을 찾을 수 없습니다'], 404);
        }

        // reward 계산 (점수 * 0.1 + 기본 보상)
        $reward = max(1, (int)($score * 0.1) + ($game->reward_base ?? 10));
        if ($result === 'lose') $reward = (int)($reward * 0.3);

        // game_sessions 저장
        $sessionId = DB::table('game_sessions')->insertGetId([
            'game_id'    => $gameId,
            'user_id'    => $user->id,
            'score'      => $score,
            'result'     => $result,
            'duration'   => $duration,
            'reward'     => $reward,
            'meta'       => json_encode(['level' => $level]),
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        // 코인 지급 (user_wallets 테이블)
        DB::table('user_wallets')
            ->where('user_id', $user->id)
            ->increment('coin_balance', $reward);
        DB::table('user_wallets')
            ->where('user_id', $user->id)
            ->increment('lifetime_earned', $reward);

        // play_count 증가
        DB::table('games')->where('id', $gameId)->increment('play_count');

        return response()->json([
            'success'    => true,
            'session_id' => $sessionId,
            'score'      => $score,
            'reward'     => $reward,
            'message'    => "{$reward}코인을 받았어요!",
        ]);
    }

    // GET /api/games/my-scores — 내 게임 기록
    public function myScores(Request $req)
    {
        $user = Auth::user();
        $gameId = $req->query('game_id');

        $query = DB::table('game_sessions as gs')
            ->join('games as g', 'gs.game_id', '=', 'g.id')
            ->select('gs.id', 'gs.game_id', 'g.name as game_name', 'gs.score',
                     'gs.result', 'gs.reward', 'gs.duration', 'gs.created_at')
            ->where('gs.user_id', $user->id)
            ->orderByDesc('gs.created_at')
            ->limit(50);

        if ($gameId) {
            $query->where('gs.game_id', $gameId);
        }

        $scores = $query->get();

        // 게임별 최고점수 요약
        $summary = DB::table('game_sessions')
            ->select('game_id', DB::raw('MAX(score) as best_score'), DB::raw('COUNT(*) as play_count'), DB::raw('SUM(reward) as total_reward'))
            ->where('user_id', $user->id)
            ->groupBy('game_id')
            ->get();

        return response()->json([
            'scores'  => $scores,
            'summary' => $summary,
        ]);
    }

    // GET /api/games/leaderboard/{gameId} — 특정 게임 리더보드
    public function gameLeaderboard($gameId)
    {
        $leaders = DB::table('game_sessions as gs')
            ->join('users as u', 'gs.user_id', '=', 'u.id')
            ->select('u.id', 'u.nickname', 'u.username',
                     DB::raw('MAX(gs.score) as best_score'),
                     DB::raw('COUNT(gs.id) as play_count'))
            ->where('gs.game_id', $gameId)
            ->groupBy('u.id', 'u.nickname', 'u.username')
            ->orderByDesc('best_score')
            ->limit(20)
            ->get();

        return response()->json($leaders);
    }

    // ---- 관리자 전용 ----

    // GET /api/admin/games — 전체 게임 목록 (관리자)
    public function adminList()
    {
        $games = DB::table('games as g')
            ->leftJoin('game_categories as gc', 'g.category_id', '=', 'gc.id')
            ->select('g.*', 'gc.name as category_name',
                     DB::raw('(SELECT COUNT(*) FROM game_sessions WHERE game_id=g.id) as session_count'),
                     DB::raw('(SELECT MAX(score) FROM game_sessions WHERE game_id=g.id) as top_score'))
            ->orderBy('g.category_id')
            ->orderBy('g.sort_order')
            ->get();

        return response()->json($games);
    }

    // PUT /api/admin/games/{id}/toggle — 게임 활성/비활성
    public function toggleActive($id)
    {
        $game = DB::table('games')->where('id', $id)->first();
        if (!$game) return response()->json(['error' => '게임 없음'], 404);
        DB::table('games')->where('id', $id)->update(['is_active' => !$game->is_active]);
        return response()->json(['success' => true, 'is_active' => !$game->is_active]);
    }

    // GET /api/admin/games/{id}/questions — 게임 문제 목록
    public function getQuestions($gameId)
    {
        $questions = DB::table('game_questions')
            ->where('game_id', $gameId)
            ->orderBy('sort_order')
            ->orderBy('id')
            ->get();
        return response()->json($questions);
    }

    // POST /api/admin/games/{id}/questions — 문제 추가
    public function addQuestion(Request $req, $gameId)
    {
        $id = DB::table('game_questions')->insertGetId([
            'game_id'    => $gameId,
            'question'   => $req->input('question'),
            'answer'     => $req->input('answer'),
            'options'    => json_encode($req->input('options', [])),
            'image_url'  => $req->input('image_url'),
            'difficulty' => $req->input('difficulty', 1),
            'is_active'  => 1,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        return response()->json(['success' => true, 'id' => $id]);
    }

    // DELETE /api/admin/questions/{id} — 문제 삭제
    public function deleteQuestion($id)
    {
        DB::table('game_questions')->where('id', $id)->delete();
        return response()->json(['success' => true]);
    }
}
