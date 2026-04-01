#!/usr/bin/env python3
import paramiko, base64, sys

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunk_size = 2000
    chunks = [enc[i:i+chunk_size] for i in range(0, len(enc), chunk_size)]
    ssh(f"rm -f /tmp/wf_chunk")
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f"cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk")
    size = ssh(f"wc -c < {path}")
    log(f"Written {path} ({size} bytes)")

# WalletController.php
wallet_ctrl = """<?php
namespace App\\Http\\Controllers\\API;
use App\\Http\\Controllers\\Controller;
use Illuminate\\Http\\Request;
use Illuminate\\Support\\Facades\\Auth;
use Illuminate\\Support\\Facades\\DB;

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
"""

# GameCategoryController.php
game_cat_ctrl = """<?php
namespace App\\Http\\Controllers\\API;
use App\\Http\\Controllers\\Controller;
use Illuminate\\Support\\Facades\\DB;

class GameCategoryController extends Controller
{
    public function index()
    {
        $categories = DB::table('game_categories')->where('is_active', 1)->orderBy('sort_order')->get();
        foreach ($categories as $cat) {
            $cat->games = DB::table('games')->where('category_id', $cat->id)->where('is_active', 1)->orderBy('sort_order')->get();
        }
        return response()->json($categories);
    }

    public function leaderboard()
    {
        $leaders = DB::table('user_wallets as w')
            ->join('users as u', 'w.user_id', '=', 'u.id')
            ->select('u.id', 'u.nickname', 'u.username', 'w.coin_balance', 'w.lifetime_earned')
            ->orderByDesc('w.lifetime_earned')->limit(20)->get();
        return response()->json($leaders);
    }
}
"""

write_file('/var/www/somekorean/app/Http/Controllers/API/WalletController.php', wallet_ctrl)
write_file('/var/www/somekorean/app/Http/Controllers/API/GameCategoryController.php', game_cat_ctrl)

# Add routes to api.php
log("\n=== Adding routes to api.php ===")
current_api = ssh('cat /var/www/somekorean/routes/api.php')
log(f"api.php lines: {len(current_api.splitlines())}")

# Check if wallet routes already exist
if 'wallet/balance' in current_api:
    log("Wallet routes already exist in api.php")
else:
    # Add public game-categories route
    public_route = """
// 게임 카테고리 (공개)
Route::get('game-categories', [\\App\\Http\\Controllers\\API\\GameCategoryController::class, 'index']);
Route::get('game-leaderboard', [\\App\\Http\\Controllers\\API\\GameCategoryController::class, 'leaderboard']);
"""
    # Add before auth middleware
    insert_marker = "// 인증 필요"
    if insert_marker in current_api:
        new_api = current_api.replace(insert_marker, public_route + "\n" + insert_marker)
        log("Adding game-categories routes before auth middleware")
    else:
        # Add at end before closing
        new_api = current_api + public_route
        log("Adding game-categories routes at end")

    # Add wallet routes inside auth middleware
    wallet_routes = """
    // 지갑
    Route::get('wallet/balance', [\\App\\Http\\Controllers\\API\\WalletController::class, 'balance']);
    Route::get('wallet/transactions', [\\App\\Http\\Controllers\\API\\WalletController::class, 'transactions']);
    Route::post('wallet/daily-bonus', [\\App\\Http\\Controllers\\API\\WalletController::class, 'dailyBonus']);
    Route::post('wallet/convert', [\\App\\Http\\Controllers\\API\\WalletController::class, 'convert']);
"""
    # Find auth middleware closing to insert before
    auth_close = "});"
    # Insert wallet routes before the last }); in auth middleware group
    # Find the Q&A routes inside middleware
    qa_marker = "    // Q&A"
    if qa_marker in new_api:
        new_api = new_api.replace(qa_marker, wallet_routes + "\n" + qa_marker)
    else:
        # Just append to the auth group
        new_api = new_api.replace("    // Auth\n", wallet_routes + "\n    // Auth\n")

    write_file('/var/www/somekorean/routes/api.php', new_api)
    log("api.php updated with wallet and game routes")

# Add admin wallet routes
if 'admin/wallets' not in current_api:
    current_api2 = ssh('cat /var/www/somekorean/routes/api.php')
    admin_routes = """
    // 지갑 관리 (어드민)
    Route::get('admin/wallets', function() {
        $wallets = \\Illuminate\\Support\\Facades\\DB::table('user_wallets as w')
            ->leftJoin('users as u', 'w.user_id', '=', 'u.id')
            ->select('w.*', 'u.username', 'u.nickname')
            ->orderByDesc('w.coin_balance')->get();
        $stats = ['total_wallets' => $wallets->count(), 'total_star' => $wallets->sum('star_balance'),
            'total_gem' => $wallets->sum('gem_balance'), 'total_coin' => $wallets->sum('coin_balance')];
        return response()->json(['wallets' => $wallets, 'stats' => $stats]);
    });
    Route::get('admin/wallet-transactions', function() {
        return response()->json(\\Illuminate\\Support\\Facades\\DB::table('wallet_transactions')->orderByDesc('created_at')->paginate(50));
    });
"""
    # Insert before last closing of auth middleware
    if '    // Q&A' in current_api2:
        new_api2 = current_api2.replace('    // Q&A', admin_routes + '\n    // Q&A')
        write_file('/var/www/somekorean/routes/api.php', new_api2)
        log("Admin wallet routes added")

# Update router/index.js - add new game routes
log("\n=== Updating router ===")
router_content = ssh('cat /var/www/somekorean/resources/js/router/index.js')

new_routes = """
    { path: '/games/car-jump', component: () => import('../pages/games/GameCarJump.vue'), name: 'game-carjump' },
    { path: '/games/number-memory', component: () => import('../pages/games/GameNumberMemory.vue'), name: 'game-numbermem' },
    { path: '/games/wordle', component: () => import('../pages/games/GameWordle.vue'), name: 'game-wordle' },"""

if 'game-carjump' not in router_content:
    # Add after the omok route
    omok_line = "    { path: '/games/omok',"
    if omok_line in router_content:
        new_router = router_content.replace(omok_line, new_routes + "\n" + omok_line)
        write_file('/var/www/somekorean/resources/js/router/index.js', new_router)
        log("New game routes added to router")
    else:
        log("Could not find omok route to insert after")
else:
    log("Game routes already in router")

# Add AdminWallet to admin router children
if 'admin-wallet' not in router_content:
    wallet_route = "            { path: 'wallet', component: () => import('../pages/admin/AdminWallet.vue'), name: 'admin-wallet' },"
    games_admin = "            { path: 'games-admin',"
    router_content2 = ssh('cat /var/www/somekorean/resources/js/router/index.js')
    if games_admin in router_content2:
        new_router2 = router_content2.replace(games_admin, wallet_route + "\n" + games_admin)
        write_file('/var/www/somekorean/resources/js/router/index.js', new_router2)
        log("AdminWallet route added to admin children")

# Check AdminLayout for wallet menu
log("\n=== Checking AdminLayout ===")
admin_layout = ssh('grep -n "wallet\|지갑\|games-admin" /var/www/somekorean/resources/js/pages/admin/AdminLayout.vue | head -10')
log("AdminLayout wallet/games refs: " + admin_layout)

c.close()
log("\nDone!")
