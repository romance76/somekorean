import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')
sftp = ssh.open_sftp()

def run(cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def write_file(path, content):
    with sftp.open(path, 'w') as f:
        f.write(content.encode('utf-8'))

project_root = "/var/www/somekorean"
print("=== Connected, running JWT-based API tests ===")

php_tests = r"""<?php
require __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

$results = [];

function api($method, $url, $token = null, $data = []) {
    $ch = curl_init();
    $headers = ['Content-Type: application/json', 'Accept: application/json'];
    if ($token) $headers[] = 'Authorization: Bearer ' . $token;

    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://somekorean.com' . $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
    ]);

    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    } elseif (in_array($method, ['PUT','PATCH','DELETE'])) {
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        if (!empty($data)) curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    }

    $resp = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $body = json_decode($resp, true);
    if (!$body && $resp) $body = substr($resp, 0, 500);
    return ['status' => $code, 'body' => $body, 'raw' => substr($resp ?? '', 0, 500)];
}

function do_login($email, $password) {
    // Try JWT login
    $r = api('POST', '/api/auth/login', null, ['email' => $email, 'password' => $password]);
    if ($r['status'] === 200 && is_array($r['body'])) {
        $tok = $r['body']['token'] ?? $r['body']['access_token'] ?? null;
        if (!$tok && isset($r['body']['data'])) {
            $tok = $r['body']['data']['token'] ?? $r['body']['data']['access_token'] ?? null;
        }
        if ($tok) return $tok;
    }
    // Try other login endpoints
    $r2 = api('POST', '/api/login', null, ['email' => $email, 'password' => $password]);
    if ($r2['status'] === 200 && is_array($r2['body'])) {
        return $r2['body']['token'] ?? $r2['body']['access_token'] ?? null;
    }
    return null;
}

function test_assert($label, $method, $url, $token, $data, $expected, $category, $user, &$results, $extra = []) {
    $r = api($method, $url, $token, $data);
    $status = $r['status'];
    $expected_arr = is_array($expected) ? $expected : [$expected];
    $body_str = is_array($r['body']) ? json_encode($r['body']) : (string)$r['body'];

    if ($status >= 500) {
        $pass = 'SERVER_ERROR';
    } elseif ($status === 0) {
        $pass = 'CONNECTION_ERROR';
    } elseif (in_array($status, $expected_arr)) {
        $pass = 'PASS';
    } elseif ($status === 404 && !in_array(404, $expected_arr)) {
        $pass = 'N/A_404';
    } else {
        $pass = 'FAIL';
    }

    $icon = $pass === 'PASS' ? 'OK' : ($pass === 'N/A_404' ? '--' : '!!');
    echo "[$icon] $label => HTTP $status (exp:" . implode('/', $expected_arr) . ")\n";
    if (in_array($pass, ['FAIL','SERVER_ERROR'])) {
        echo "  >> " . substr($body_str, 0, 300) . "\n";
    }

    $entry = array_merge([
        'label' => $label,
        'method' => $method,
        'endpoint' => $url,
        'status' => $status,
        'pass' => $pass,
        'expected' => $expected,
        'category' => $category,
        'user' => $user,
        'body_preview' => substr($body_str, 0, 400),
        'security_risk' => 'none',
    ], $extra);

    // Mark security risk
    if (in_array($status, [200,201]) && in_array(403, $expected_arr)) {
        $entry['security_risk'] = 'HIGH - Auth bypass: ' . $method . ' ' . $url . ' returned ' . $status . ' instead of 403';
        $entry['pass'] = 'FAIL_SECURITY_BUG';
    }

    $results[] = $entry;
    return $r;
}

// =================== LOGIN ALL USERS ===================
$user_defs = [
    ['username'=>'testadmin1','email'=>'testadmin1@test.com','category'=>'admin_tester','id'=>299],
    ['username'=>'testadmin2','email'=>'testadmin2@test.com','category'=>'admin_tester','id'=>300],
    ['username'=>'user01','email'=>'user01@test.com','category'=>'general','id'=>301],
    ['username'=>'user02','email'=>'user02@test.com','category'=>'general','id'=>302],
    ['username'=>'user03','email'=>'user03@test.com','category'=>'general','id'=>303],
    ['username'=>'user04','email'=>'user04@test.com','category'=>'general','id'=>304],
    ['username'=>'user05','email'=>'user05@test.com','category'=>'general','id'=>305],
    ['username'=>'user06','email'=>'user06@test.com','category'=>'general','id'=>306],
    ['username'=>'user07','email'=>'user07@test.com','category'=>'general','id'=>307],
    ['username'=>'user08','email'=>'user08@test.com','category'=>'general','id'=>308],
    ['username'=>'user09','email'=>'user09@test.com','category'=>'general','id'=>309],
    ['username'=>'user10','email'=>'user10@test.com','category'=>'general','id'=>310],
    ['username'=>'oper01','email'=>'oper01@test.com','category'=>'operator','id'=>311],
    ['username'=>'oper02','email'=>'oper02@test.com','category'=>'operator','id'=>312],
    ['username'=>'oper03','email'=>'oper03@test.com','category'=>'operator','id'=>313],
    ['username'=>'points01','email'=>'points01@test.com','category'=>'points_analyst','id'=>314],
    ['username'=>'points02','email'=>'points02@test.com','category'=>'points_analyst','id'=>315],
    ['username'=>'points03','email'=>'points03@test.com','category'=>'points_analyst','id'=>316],
    ['username'=>'points04','email'=>'points04@test.com','category'=>'points_analyst','id'=>317],
    ['username'=>'points05','email'=>'points05@test.com','category'=>'points_analyst','id'=>318],
];

$tokens = [];
$ids = [];
$password = 'Test1234!';

echo "=== Logging in all users ===\n";

// Test login endpoint format first
$r_test = api('POST', '/api/auth/login', null, ['email' => 'testadmin1@test.com', 'password' => $password]);
echo "Login test: HTTP {$r_test['status']}\n";
echo "Login body: " . substr(json_encode($r_test['body']), 0, 500) . "\n\n";

foreach ($user_defs as $u) {
    $tok = do_login($u['email'], $password);
    if ($tok) {
        $tokens[$u['username']] = $tok;
        $ids[$u['username']] = $u['id'];
        echo "Logged in: {$u['username']} (token: " . substr($tok, 0, 30) . "...)\n";
    } else {
        echo "FAILED login: {$u['username']}\n";
    }
}

$logged_in = count($tokens);
echo "\nLogged in $logged_in / " . count($user_defs) . " users\n\n";

if ($logged_in === 0) {
    echo "ERROR: No users logged in. Check auth endpoint.\n";
    // Debug: check what /api/auth/login returns for one user
    $debug = api('POST', '/api/auth/login', null, ['email' => 'user01@test.com', 'password' => 'Test1234!']);
    echo "Debug login response: HTTP {$debug['status']}\n";
    echo "Raw: " . $debug['raw'] . "\n";
    // Also try to get me without token
    $debug2 = api('GET', '/api/auth/me', null, []);
    echo "GET /api/auth/me (no token): HTTP {$debug2['status']}\n";
    file_put_contents('/tmp/ct_test_results.json', json_encode([], JSON_PRETTY_PRINT));
    echo "\nRESULTS_START\n[]\nRESULTS_END\n";
    exit;
}

// ===================== ADMIN TESTS =====================
echo "=== ADMIN ACCESS TESTS ===\n";
$admin_testers = ['testadmin1', 'testadmin2'];
$admin_endpoints = [
    '/api/admin/stats', '/api/admin/members', '/api/admin/users',
    '/api/admin/dashboard', '/api/admin/posts', '/api/admin/jobs',
    '/api/admin/activity',
];

foreach ($admin_testers as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }
    foreach ($admin_endpoints as $ep) {
        test_assert("[$u] GET $ep", 'GET', $ep, $tok, [], [401,403], 'admin_tester', $u, $results);
    }
}

// ===================== GENERAL USER TESTS =====================
echo "\n=== GENERAL USER TESTS ===\n";
$created_posts = [];
$created_jobs = [];
$created_markets = [];

// First, get a valid board_id
$boards_r = api('GET', '/api/boards', null, []);
$board_id = 1;
if ($boards_r['status'] === 200 && is_array($boards_r['body'])) {
    $bd = $boards_r['body'];
    $list = $bd['data'] ?? $bd;
    if (is_array($list) && !empty($list)) {
        $board_id = $list[0]['id'] ?? 1;
    }
}
echo "Using board_id=$board_id\n";

foreach (['user01','user02','user03'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }
    $uid = $ids[$u] ?? 301;

    echo "\n-- $u --\n";

    // Profile
    $r = test_assert("[$u] GET /api/auth/me (profile)", 'GET', '/api/auth/me', $tok, [], [200], 'general_user', $u, $results);
    $pts = null;
    if ($r['status'] === 200 && is_array($r['body'])) {
        $pts = $r['body']['points_total'] ?? $r['body']['points'] ?? $r['body']['data']['points'] ?? 'N/A';
        echo "  Points: $pts\n";
    }

    // Create post
    $r = api('POST', '/api/posts', $tok, [
        'board_id' => $board_id,
        'title' => "Test post by $u - " . time(),
        'content' => "Content posted by $u for QA testing",
    ]);
    $post_id = null;
    if (in_array($r['status'], [200,201])) {
        $b = $r['body'];
        $post_id = is_array($b) ? ($b['post']['id'] ?? $b['id'] ?? $b['data']['id'] ?? null) : null;
        if ($post_id) $created_posts[$u] = $post_id;
    }
    $pass = in_array($r['status'],[200,201]) ? 'PASS' : 'FAIL';
    echo "[$pass] [$u] POST /api/posts => HTTP {$r['status']} post_id=$post_id\n";
    $results[] = ['label'=>"[$u] POST /api/posts",'method'=>'POST','endpoint'=>'/api/posts','status'=>$r['status'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$post_id,'body_preview'=>substr(json_encode($r['body']),0,400),'security_risk'=>'none'];
    if ($pass === 'FAIL') echo "  >> " . substr(json_encode($r['body']),0,300) . "\n";

    // Create comment
    if ($post_id) {
        $r2 = api('POST', "/api/posts/{$post_id}/comments", $tok, ['content' => "Comment by $u"]);
        $pass2 = in_array($r2['status'],[200,201]) ? 'PASS' : 'FAIL';
        echo "[$pass2] [$u] POST comment => HTTP {$r2['status']}\n";
        $results[] = ['label'=>"[$u] POST comment on post {$post_id}",'method'=>'POST','endpoint'=>"/api/posts/{$post_id}/comments",'status'=>$r2['status'],'pass'=>$pass2,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'body_preview'=>substr(json_encode($r2['body']),0,300),'security_risk'=>'none'];
        if ($pass2 === 'FAIL') echo "  >> " . substr(json_encode($r2['body']),0,300) . "\n";
    }

    // Create job
    $r3 = api('POST', '/api/jobs', $tok, [
        'title' => "Job by $u " . time(),
        'content' => "Job description by $u",
        'company_name' => 'Test Corp',
        'region' => 'New York',
        'job_type' => 'full_time',
    ]);
    $job_id = null;
    if (in_array($r3['status'],[200,201])) {
        $b3 = $r3['body'];
        $job_id = is_array($b3) ? ($b3['job']['id'] ?? $b3['id'] ?? $b3['data']['id'] ?? null) : null;
        if ($job_id) $created_jobs[$u] = $job_id;
    }
    $pass3 = in_array($r3['status'],[200,201]) ? 'PASS' : 'FAIL';
    echo "[$pass3] [$u] POST /api/jobs => HTTP {$r3['status']} job_id=$job_id\n";
    $results[] = ['label'=>"[$u] POST /api/jobs",'method'=>'POST','endpoint'=>'/api/jobs','status'=>$r3['status'],'pass'=>$pass3,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$job_id,'body_preview'=>substr(json_encode($r3['body']),0,400),'security_risk'=>'none'];
    if ($pass3 === 'FAIL') echo "  >> " . substr(json_encode($r3['body']),0,300) . "\n";

    // Create market
    $r4 = api('POST', '/api/market', $tok, [
        'title' => "Market item by $u " . time(),
        'description' => "Market desc by $u",
        'price' => 100,
        'item_type' => 'used',
        'category' => 'electronics',
    ]);
    $market_id = null;
    if (in_array($r4['status'],[200,201])) {
        $b4 = $r4['body'];
        $market_id = is_array($b4) ? ($b4['item']['id'] ?? $b4['id'] ?? $b4['data']['id'] ?? null) : null;
        if ($market_id) $created_markets[$u] = $market_id;
    }
    $pass4 = in_array($r4['status'],[200,201]) ? 'PASS' : 'FAIL';
    echo "[$pass4] [$u] POST /api/market => HTTP {$r4['status']} market_id=$market_id\n";
    $results[] = ['label'=>"[$u] POST /api/market",'method'=>'POST','endpoint'=>'/api/market','status'=>$r4['status'],'pass'=>$pass4,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$market_id,'body_preview'=>substr(json_encode($r4['body']),0,400),'security_risk'=>'none'];
    if ($pass4 === 'FAIL') echo "  >> " . substr(json_encode($r4['body']),0,300) . "\n";

    // Points endpoints
    foreach (['/api/points/balance', '/api/points/history'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'points_check','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400),'security_risk'=>'none'];
    }

    // Game endpoints
    foreach (['/api/games/rooms', '/api/games/leaderboard', '/api/games/shop', '/api/games/my-scores'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'game_check','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400),'security_risk'=>'none'];
    }
}

// ===================== CROSS-USER AUTH TESTS =====================
echo "\n=== CROSS-USER AUTHORIZATION TESTS ===\n";

if (!empty($created_posts['user01']) && !empty($tokens['user02'])) {
    $pid = $created_posts['user01'];
    $tok2 = $tokens['user02'];
    test_assert("user02 PUT /api/posts/{$pid} (user01 post)", 'PUT', "/api/posts/{$pid}", $tok2, ['title'=>'HACKED','content'=>'HACKED'], [401,403], 'cross_user_auth', 'user02 vs user01', $results);
    test_assert("user02 DELETE /api/posts/{$pid} (user01 post)", 'DELETE', "/api/posts/{$pid}", $tok2, [], [401,403], 'cross_user_auth', 'user02 vs user01', $results);
}
if (!empty($created_posts['user01']) && !empty($tokens['testadmin1'])) {
    $pid = $created_posts['user01'];
    $tok_adm = $tokens['testadmin1'];
    test_assert("testadmin1 PUT /api/posts/{$pid} (user01 post)", 'PUT', "/api/posts/{$pid}", $tok_adm, ['title'=>'Admin Hacked'], [401,403], 'admin_tester_cross', 'testadmin1 vs user01', $results);
    test_assert("testadmin1 DELETE /api/posts/{$pid} (user01 post)", 'DELETE', "/api/posts/{$pid}", $tok_adm, [], [401,403], 'admin_tester_cross', 'testadmin1 vs user01', $results);
}
if (!empty($created_jobs['user01']) && !empty($tokens['user02'])) {
    $jid = $created_jobs['user01'];
    $tok2 = $tokens['user02'];
    test_assert("user02 PUT /api/jobs/{$jid} (user01 job)", 'PUT', "/api/jobs/{$jid}", $tok2, ['title'=>'HACKED job'], [401,403], 'cross_user_auth', 'user02 vs user01', $results);
    test_assert("user02 DELETE /api/jobs/{$jid} (user01 job)", 'DELETE', "/api/jobs/{$jid}", $tok2, [], [401,403], 'cross_user_auth', 'user02 vs user01', $results);
}
if (!empty($created_jobs['user01']) && !empty($tokens['testadmin2'])) {
    $jid = $created_jobs['user01'];
    $tok_adm = $tokens['testadmin2'];
    test_assert("testadmin2 PUT /api/jobs/{$jid} (user01 job)", 'PUT', "/api/jobs/{$jid}", $tok_adm, ['title'=>'Admin Hacked job'], [401,403], 'admin_tester_cross', 'testadmin2 vs user01', $results);
}
if (!empty($created_markets['user01']) && !empty($tokens['user02'])) {
    $mid = $created_markets['user01'];
    $tok2 = $tokens['user02'];
    test_assert("user02 PUT /api/market/{$mid} (user01 item)", 'PUT', "/api/market/{$mid}", $tok2, ['title'=>'HACKED market'], [401,403], 'cross_user_auth', 'user02 vs user01', $results);
    test_assert("user02 DELETE /api/market/{$mid} (user01 item)", 'DELETE', "/api/market/{$mid}", $tok2, [], [401,403], 'cross_user_auth', 'user02 vs user01', $results);
}

// ===================== OPERATOR TESTS =====================
echo "\n=== OPERATOR TESTS ===\n";
foreach (['oper01','oper02'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }

    $r = test_assert("[$u] GET /api/auth/me", 'GET', '/api/auth/me', $tok, [], [200], 'operator_test', $u, $results);

    foreach (['/api/moderator', '/api/reports', '/api/admin/moderate'] as $ep) {
        test_assert("[$u] GET $ep", 'GET', $ep, $tok, [], [200], 'operator_test', $u, $results);
    }

    // Can operators post content? (should work as regular users)
    $r_post = api('POST', '/api/posts', $tok, ['board_id'=>$board_id,'title'=>"Oper post by $u",'content'=>"Operator test content"]);
    $pass_p = in_array($r_post['status'],[200,201]) ? 'PASS' : 'FAIL';
    echo "[$pass_p] [$u] POST /api/posts (operator creates post) => HTTP {$r_post['status']}\n";
    $results[] = ['label'=>"[$u] POST /api/posts (operator)",'method'=>'POST','endpoint'=>'/api/posts','status'=>$r_post['status'],'pass'=>$pass_p,'expected'=>[200,201],'category'=>'operator_test','user'=>$u,'body_preview'=>substr(json_encode($r_post['body']),0,300),'security_risk'=>'none'];
}

// ===================== POINTS ANALYST TESTS =====================
echo "\n=== POINTS ANALYST TESTS ===\n";
foreach (['points01','points02'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }
    $uid = $ids[$u] ?? 314;

    echo "\n-- $u --\n";

    // Check profile for points
    $r_me = api('GET', '/api/auth/me', $tok);
    $pts = null;
    if ($r_me['status'] === 200 && is_array($r_me['body'])) {
        $pts = $r_me['body']['points_total'] ?? $r_me['body']['points'] ?? 'N/A';
    }
    echo "Profile: HTTP {$r_me['status']} | points_total=$pts\n";
    $results[] = ['label'=>"[$u] GET /api/auth/me (points check)",'method'=>'GET','endpoint'=>'/api/auth/me','status'=>$r_me['status'],'pass'=>$r_me['status']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_analyst','user'=>$u,'points_value'=>$pts,'body_preview'=>substr(json_encode($r_me['body']),0,500),'security_risk'=>'none'];

    // Points endpoints
    foreach (['/api/points/balance', '/api/points/history'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        echo "[$pass] GET $ep => HTTP {$r['status']}\n";
        if ($r['status'] !== 404) {
            $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'points_analyst','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400),'security_risk'=>'none'];
        }
        if ($r['status'] === 200) {
            echo "  Data: " . substr(json_encode($r['body']), 0, 300) . "\n";
        }
    }

    // Check-in
    $r_ci = api('POST', '/api/points/checkin', $tok);
    $pass_ci = in_array($r_ci['status'],[200,400]) ? 'PASS' : 'INFO';
    echo "[$pass_ci] POST /api/points/checkin => HTTP {$r_ci['status']}\n";
    $results[] = ['label'=>"[$u] POST /api/points/checkin",'method'=>'POST','endpoint'=>'/api/points/checkin','status'=>$r_ci['status'],'pass'=>$pass_ci,'expected'=>[200,400],'category'=>'points_analyst','user'=>$u,'body_preview'=>substr(json_encode($r_ci['body']),0,300),'security_risk'=>'none'];

    // Wallet endpoints
    foreach (['/api/wallet/balance', '/api/wallet/transactions'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        echo "[$pass] GET $ep => HTTP {$r['status']}\n";
        if ($r['status'] !== 404) {
            $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'points_analyst','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400),'security_risk'=>'none'];
            if ($r['status'] === 200) echo "  Data: " . substr(json_encode($r['body']),0,300) . "\n";
        }
    }

    // Daily bonus
    $r_db = api('POST', '/api/wallet/daily-bonus', $tok);
    $pass_db = in_array($r_db['status'],[200,400]) ? 'PASS' : 'INFO';
    echo "[$pass_db] POST /api/wallet/daily-bonus => HTTP {$r_db['status']}\n";
    $results[] = ['label'=>"[$u] POST /api/wallet/daily-bonus",'method'=>'POST','endpoint'=>'/api/wallet/daily-bonus','status'=>$r_db['status'],'pass'=>$pass_db,'expected'=>[200,400],'category'=>'points_analyst','user'=>$u,'body_preview'=>substr(json_encode($r_db['body']),0,300),'security_risk'=>'none'];

    // Game rooms
    foreach (['/api/games/rooms', '/api/games/leaderboard', '/api/games/shop'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        echo "[$pass] GET $ep => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'game_test','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400),'security_risk'=>'none'];
        if ($r['status'] === 200) echo "  Data: " . substr(json_encode($r['body']),0,300) . "\n";
    }

    // Create game room (uses points)
    $r_gr = api('POST', '/api/games/rooms', $tok, ['bet_points'=>100, 'max_players'=>2]);
    $pass_gr = in_array($r_gr['status'],[200,201]) ? 'PASS' : 'INFO';
    echo "[$pass_gr] POST /api/games/rooms (create game room) => HTTP {$r_gr['status']}\n";
    $results[] = ['label'=>"[$u] POST /api/games/rooms",'method'=>'POST','endpoint'=>'/api/games/rooms','status'=>$r_gr['status'],'pass'=>$pass_gr,'expected'=>[200,201],'category'=>'game_test','user'=>$u,'body_preview'=>substr(json_encode($r_gr['body']),0,400),'security_risk'=>'none'];
    if ($r_gr['status'] === 200 || $r_gr['status'] === 201) {
        echo "  Created room: " . substr(json_encode($r_gr['body']),0,300) . "\n";
    }

    // Points change after posting
    $pts_before = null;
    $r_b = api('GET', '/api/points/balance', $tok);
    if ($r_b['status']===200 && is_array($r_b['body'])) {
        $pts_before = $r_b['body']['points'] ?? null;
    }

    $r_newpost = api('POST', '/api/posts', $tok, ['board_id'=>$board_id,'title'=>"Points test post by $u",'content'=>"Testing points award on posting"]);

    $r_a = api('GET', '/api/points/balance', $tok);
    $pts_after = null;
    if ($r_a['status']===200 && is_array($r_a['body'])) {
        $pts_after = $r_a['body']['points'] ?? null;
    }
    $changed = ($pts_before !== null && $pts_after !== null && $pts_before !== $pts_after);
    echo "Points change: before=$pts_before after=$pts_after changed=" . ($changed?'YES':'NO') . " (post_status={$r_newpost['status']})\n";
    $results[] = [
        'label' => "[$u] points awarded for posting",
        'method' => 'POST',
        'endpoint' => '/api/posts',
        'status' => $r_newpost['status'],
        'pass' => 'INFO',
        'expected' => 'info',
        'category' => 'points_award_test',
        'user' => $u,
        'points_before' => $pts_before,
        'points_after' => $pts_after,
        'points_changed' => $changed,
        'post_status' => $r_newpost['status'],
        'body_preview' => '',
        'security_risk' => 'none',
    ];
}

// ===================== FINAL SUMMARY =====================
echo "\n=== FINAL SUMMARY ===\n";
$total = count($results);
$passed = count(array_filter($results, fn($r) => $r['pass'] === 'PASS'));
$failed = count(array_filter($results, fn($r) => in_array($r['pass'],['FAIL','FAIL_SECURITY_BUG'])));
$server_errs = count(array_filter($results, fn($r) => $r['pass'] === 'SERVER_ERROR' || ($r['status']??0) >= 500));
$na = count(array_filter($results, fn($r) => $r['pass'] === 'N/A_404'));
$info = count(array_filter($results, fn($r) => $r['pass'] === 'INFO'));

echo "Total: $total | PASS: $passed | FAIL: $failed | SERVER_ERR: $server_errs | N/A_404: $na | INFO: $info\n";

echo "\n--- Security Issues ---\n";
$sec = array_filter($results, fn($r) => ($r['security_risk'] ?? 'none') !== 'none');
foreach ($sec as $s) echo "!! SECURITY: {$s['security_risk']}\n";
if (empty($sec)) echo "None\n";

echo "\n--- Server Errors ---\n";
$errs = array_filter($results, fn($r) => $r['pass'] === 'SERVER_ERROR' || ($r['status']??0) >= 500);
foreach ($errs as $e) {
    echo "500: {$e['method']} {$e['endpoint']}\n";
    echo "  " . substr($e['body_preview'],0,300) . "\n";
}
if (empty($errs)) echo "None\n";

echo "\n--- FAIL (non-security) ---\n";
$fails = array_filter($results, fn($r) => $r['pass'] === 'FAIL');
foreach ($fails as $f) {
    echo "FAIL: {$f['label']} => HTTP {$f['status']}\n";
    echo "  " . substr($f['body_preview'],0,200) . "\n";
}
if (empty($fails)) echo "None\n";

file_put_contents('/tmp/ct_test_results.json', json_encode($results, JSON_PRETTY_PRINT));
echo "\nRESULTS_START\n";
echo json_encode($results);
echo "\nRESULTS_END\n";
"""

write_file(f'{project_root}/ct_run_tests.php', php_tests)
print("Running tests with JWT auth...")

out, err = run(f"cd {project_root} && php ct_run_tests.php 2>&1", timeout=300)
print(out.encode('ascii', errors='replace').decode('ascii')[:20000])
if err:
    print("STDERR:", err[:2000])

# Parse results
test_results = []
if 'RESULTS_START' in out and 'RESULTS_END' in out:
    json_section = out.split('RESULTS_START\n')[1].split('\nRESULTS_END')[0]
    try:
        test_results = json.loads(json_section)
        print(f"\nParsed {len(test_results)} test results")
    except Exception as e:
        print(f"Parse error: {e}")
        print(json_section[:500])

# Cleanup
run(f"rm -f {project_root}/ct_run_tests.php")

# Compile final report
users_created = [
    {'username':'testadmin1','email':'testadmin1@test.com','id':299,'password':'Test1234!','category':'admin_tester'},
    {'username':'testadmin2','email':'testadmin2@test.com','id':300,'password':'Test1234!','category':'admin_tester'},
    {'username':'user01','email':'user01@test.com','id':301,'password':'Test1234!','category':'general'},
    {'username':'user02','email':'user02@test.com','id':302,'password':'Test1234!','category':'general'},
    {'username':'user03','email':'user03@test.com','id':303,'password':'Test1234!','category':'general'},
    {'username':'user04','email':'user04@test.com','id':304,'password':'Test1234!','category':'general'},
    {'username':'user05','email':'user05@test.com','id':305,'password':'Test1234!','category':'general'},
    {'username':'user06','email':'user06@test.com','id':306,'password':'Test1234!','category':'general'},
    {'username':'user07','email':'user07@test.com','id':307,'password':'Test1234!','category':'general'},
    {'username':'user08','email':'user08@test.com','id':308,'password':'Test1234!','category':'general'},
    {'username':'user09','email':'user09@test.com','id':309,'password':'Test1234!','category':'general'},
    {'username':'user10','email':'user10@test.com','id':310,'password':'Test1234!','category':'general'},
    {'username':'oper01','email':'oper01@test.com','id':311,'password':'Test1234!','category':'operator'},
    {'username':'oper02','email':'oper02@test.com','id':312,'password':'Test1234!','category':'operator'},
    {'username':'oper03','email':'oper03@test.com','id':313,'password':'Test1234!','category':'operator'},
    {'username':'points01','email':'points01@test.com','id':314,'password':'Test1234!','category':'points_analyst'},
    {'username':'points02','email':'points02@test.com','id':315,'password':'Test1234!','category':'points_analyst'},
    {'username':'points03','email':'points03@test.com','id':316,'password':'Test1234!','category':'points_analyst'},
    {'username':'points04','email':'points04@test.com','id':317,'password':'Test1234!','category':'points_analyst'},
    {'username':'points05','email':'points05@test.com','id':318,'password':'Test1234!','category':'points_analyst'},
]

security_bugs = [r for r in test_results if r.get('security_risk','none') != 'none']
server_errs = [r for r in test_results if r.get('pass') == 'SERVER_ERROR' or r.get('status',0) >= 500]
real_fails = [r for r in test_results if r.get('pass') in ['FAIL','FAIL_SECURITY_BUG']]

final = {
    'summary': {
        'users_created': 20,
        'total_tests': len(test_results),
        'passed': len([r for r in test_results if r.get('pass') == 'PASS']),
        'failed': len(real_fails),
        'server_errors': len(server_errs),
        'security_bugs': len(security_bugs),
        'missing_features_404': len([r for r in test_results if r.get('pass') == 'N/A_404']),
    },
    'users': users_created,
    'test_results': test_results,
    'security_bugs': security_bugs,
    'server_errors': server_errs,
    'failed_tests': real_fails,
}

report_path = 'C:/Users/Admin/Desktop/somekorean/comprehensive_test_report.json'
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print(f"\n=== FINAL REPORT ===")
print(json.dumps(final['summary'], indent=2))
print(f"\nFull report saved to: {report_path}")

ssh.close()
