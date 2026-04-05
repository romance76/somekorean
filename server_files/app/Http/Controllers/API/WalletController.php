<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class WalletController extends Controller
{
    private function getOrCreateWallet($userId)
    {
        $wallet = DB::table('user_wallets')->where('user_id', $userId)->first();
        if (!$wallet) {
            DB::table('user_wallets')->insert([
                'user_id' => $userId,
                'star_balance' => 0, 'gem_balance' => 0,
                'coin_balance' => 1000, 'chip_balance' => 0,
                'lifetime_earned' => 1000,
                'created_at' => now(), 'updated_at' => now(),
            ]);
            DB::table('wallet_transactions')->insert([
                'user_id' => $userId, 'type' => 'signup', 'currency' => 'coin',
                'amount' => 1000, 'balance_after' => 1000,
                'description' => '가입 보너스',
                'created_at' => now(), 'updated_at' => now(),
            ]);
            $wallet = DB::table('user_wallets')->where('user_id', $userId)->first();
        }
        return $wallet;
    }

    public function balance()
    {
        $userId = Auth::id();
        $wallet = $this->getOrCreateWallet($userId);
        return response()->json([
            'star' => (int)$wallet->star_balance, 'gem' => (int)$wallet->gem_balance,
            'coin' => (int)$wallet->coin_balance, 'chip' => (int)$wallet->chip_balance,
        ]);
    }

    public function transactions()
    {
        $txs = DB::table('wallet_transactions')
            ->where('user_id', Auth::id())
            ->orderByDesc('created_at')->paginate(20);
        return response()->json($txs);
    }

    public function dailyBonus()
    {
        $userId = Auth::id();
        $claimed = DB::table('wallet_transactions')
            ->where('user_id', $userId)->where('type', 'daily')
            ->whereDate('created_at', now()->toDateString())->exists();
        if ($claimed) return response()->json(['error' => '오늘 이미 출석 보너스를 받았습니다.'], 400);
        $wallet = $this->getOrCreateWallet($userId);
        $bonus = 50;
        DB::table('user_wallets')->where('user_id', $userId)->update([
            'coin_balance' => $wallet->coin_balance + $bonus,
            'lifetime_earned' => $wallet->lifetime_earned + $bonus,
            'updated_at' => now(),
        ]);
        DB::table('wallet_transactions')->insert([
            'user_id' => $userId, 'type' => 'daily', 'currency' => 'coin',
            'amount' => $bonus, 'balance_after' => $wallet->coin_balance + $bonus,
            'description' => '일일 출석 보너스',
            'created_at' => now(), 'updated_at' => now(),
        ]);
        return response()->json(['message' => '출석 보너스 +' . $bonus . ' COIN!', 'coin' => $wallet->coin_balance + $bonus]);
    }

    public function convert(Request $request)
    {
        $request->validate(['from' => 'required|in:gem,coin', 'to' => 'required|in:coin,chip', 'amount' => 'required|integer|min:1']);
        $userId = Auth::id();
        $wallet = $this->getOrCreateWallet($userId);
        $from = $request->from; $to = $request->to; $amount = (int)$request->amount;
        $rates = ['gem_to_coin' => ['rate' => 0.1, 'min' => 1000], 'coin_to_chip' => ['rate' => 0.001, 'min' => 1000]];
        $key = $from . '_to_' . $to;
        if (!isset($rates[$key])) return response()->json(['error' => '지원하지 않는 환전입니다.'], 400);
        $rule = $rates[$key];
        if ($amount < $rule['min']) return response()->json(['error' => '최소 ' . $rule['min'] . ' 필요'], 400);
        if ((int)$wallet->{$from . '_balance'} < $amount) return response()->json(['error' => '잔액 부족'], 400);
        $toAmount = (int)($amount * $rule['rate']);
        if ($toAmount < 1) return response()->json(['error' => '환전 결과가 너무 작습니다.'], 400);
        DB::table('user_wallets')->where('user_id', $userId)->update([
            $from . '_balance' => DB::raw($from . '_balance - ' . $amount),
            $to . '_balance' => DB::raw($to . '_balance + ' . $toAmount),
            'updated_at' => now(),
        ]);
        $wallet = $this->getOrCreateWallet($userId);
        return response()->json(['message' => "환전: {$amount} " . strtoupper($from) . " → {$toAmount} " . strtoupper($to), 'wallet' => [
            'star' => (int)$wallet->star_balance, 'gem' => (int)$wallet->gem_balance,
            'coin' => (int)$wallet->coin_balance, 'chip' => (int)$wallet->chip_balance,
        ]]);
    }

    public function stars()
    {
        $userId = Auth::id();
        $wallet = $this->getOrCreateWallet($userId);
        return response()->json(['stars' => (int)$wallet->star_balance]);
    }

    public function earnStars(Request $request)
    {
        $userId = Auth::id();
        $stars = (int)$request->input('stars', 0);
        $game = $request->input('game', 'unknown');
        $score = (int)$request->input('score', 0);

        if ($stars <= 0) return response()->json(['error' => '별이 없습니다'], 400);
        if ($stars > 100) $stars = 100; // cap

        $wallet = $this->getOrCreateWallet($userId);
        DB::table('user_wallets')->where('user_id', $userId)->update([
            'star_balance' => $wallet->star_balance + $stars,
            'lifetime_earned' => $wallet->lifetime_earned + $stars,
            'updated_at' => now(),
        ]);
        DB::table('wallet_transactions')->insert([
            'user_id' => $userId, 'type' => 'earn', 'currency' => 'star',
            'amount' => $stars, 'balance_after' => $wallet->star_balance + $stars,
            'description' => "{$game} 게임 보상 (점수: {$score})",
            'created_at' => now(), 'updated_at' => now(),
        ]);
        return response()->json([
            'success' => true,
            'stars' => $wallet->star_balance + $stars,
            'message' => "+{$stars} STAR!",
        ]);
    }

    public static function reward($userId, $currency, $amount, $description, $gameId = null)
    {
        $wallet = DB::table('user_wallets')->where('user_id', $userId)->first();
        if (!$wallet) return;
        DB::table('user_wallets')->where('user_id', $userId)->update([
            $currency . '_balance' => DB::raw($currency . '_balance + ' . $amount),
            'lifetime_earned' => DB::raw('lifetime_earned + ' . $amount),
            'updated_at' => now(),
        ]);
        $newBalance = (int)DB::table('user_wallets')->where('user_id', $userId)->value($currency . '_balance');
        DB::table('wallet_transactions')->insert([
            'user_id' => $userId, 'type' => 'earn', 'currency' => $currency,
            'amount' => $amount, 'balance_after' => $newBalance,
            'game_id' => $gameId, 'description' => $description,
            'created_at' => now(), 'updated_at' => now(),
        ]);
    }
}
