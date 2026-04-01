<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Checkin;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class PointController extends Controller
{
    public function balance()
    {
        $user = Auth::user();
        $checkedInToday = \App\Models\Checkin::where('user_id', $user->id)
            ->where('checkin_date', today())
            ->exists();
        return response()->json([
            'points'          => $user->points_total,
            'points_total'    => $user->points_total,
            'cash'            => $user->cash_balance,
            'level'           => $user->level,
            'checked_in_today'=> $checkedInToday,
        ]);
    }

    public function history(Request $request)
    {
        $logs = Auth::user()->pointLogs()
            ->orderByDesc('created_at')
            ->paginate(20);
        return response()->json($logs);
    }

    public function checkin()
    {
        $user = Auth::user();
        $today = today();

        if (Checkin::where('user_id', $user->id)->where('checkin_date', $today)->exists()) {
            return response()->json(['message' => '오늘은 이미 출석체크를 했습니다.'], 400);
        }

        // 연속 출석 계산
        $yesterday = Checkin::where('user_id', $user->id)
            ->where('checkin_date', $today->copy()->subDay())
            ->first();
        $streak = $yesterday ? $yesterday->streak_days + 1 : 1;

        Checkin::create([
            'user_id'     => $user->id,
            'checkin_date'=> $today,
            'streak_days' => $streak,
        ]);

        $points = 10;
        $memo = '출석체크';
        if ($streak % 7 === 0) {
            $points += 50;
            $memo .= ' (7일 연속 보너스)';
        }

        $user->addPoints($points, 'checkin', 'earn', null, $memo);

        return response()->json([
            'message' => "출석체크 완료! +{$points}P",
            'streak'  => $streak,
            'points'  => $user->fresh()->points_total,
        ]);
    }

    public function convert(Request $request)
    {
        $request->validate(['points' => 'required|integer|min:5000']);
        $user = Auth::user();
        $points = $request->points;

        if ($points % 1000 !== 0) {
            return response()->json(['message' => '1,000P 단위로만 전환 가능합니다.'], 400);
        }
        if ($user->points_total < $points) {
            return response()->json(['message' => '포인트가 부족합니다.'], 400);
        }

        // 월 한도 체크 (50,000P)
        $monthConverted = $user->pointLogs()
            ->where('action', 'convert')
            ->whereMonth('created_at', now()->month)
            ->sum('amount');
        if (abs($monthConverted) + $points > 50000) {
            return response()->json(['message' => '월 전환 한도(50,000P)를 초과합니다.'], 400);
        }

        $cash = $points / 1000;
        $user->decrement('points_total', $points);
        $user->increment('cash_balance', $cash);
        $user->refresh();

        $user->pointLogs()->create([
            'type'         => 'convert',
            'action'       => 'convert',
            'amount'       => -$points,
            'balance_after'=> $user->points_total,
            'memo'         => "{$points}P → \${$cash} 캐시 전환",
        ]);

        return response()->json([
            'message' => "{$points}P를 \${$cash} 캐시로 전환했습니다.",
            'points'  => $user->points_total,
            'cash'    => $user->cash_balance,
        ]);
    }
}
