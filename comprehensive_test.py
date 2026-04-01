import paramiko
import sys
import json
import time

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

print("=== Connected to server ===")

# Step 1: Find the Laravel project root
out, err = run("find /var/www -name 'artisan' 2>/dev/null | head -5")
print("Artisan locations:", out.strip())

artisan_paths = [p.strip() for p in out.strip().split('\n') if p.strip()]
if not artisan_paths:
    project_root = "/var/www/html"
else:
    project_root = artisan_paths[0].replace('/artisan', '')

print(f"Project root: {project_root}")

# Step 2: Get all routes
print("\n=== Getting all routes ===")
out, err = run(f"cd {project_root} && php artisan route:list --json 2>/dev/null", timeout=120)
print(f"Routes output length: {len(out)} chars")

write_file('/tmp/routes_full.json', out)

try:
    routes_data = json.loads(out)
    print(f"Total routes: {len(routes_data)}")

    admin_routes = [r for r in routes_data if 'admin' in r.get('uri','').lower()]
    point_routes = [r for r in routes_data if 'point' in r.get('uri','').lower() or 'point' in str(r.get('action','')).lower()]
    game_routes = [r for r in routes_data if 'game' in r.get('uri','').lower() or 'game' in str(r.get('action','')).lower()]
    auth_routes = [r for r in routes_data if 'login' in r.get('uri','').lower() or 'register' in r.get('uri','').lower()]

    print(f"\nAdmin routes ({len(admin_routes)}):")
    for r in admin_routes[:30]:
        print(f"  {r.get('method','')[:8]:8} {r.get('uri','')}")

    print(f"\nPoints routes ({len(point_routes)}):")
    for r in point_routes[:20]:
        print(f"  {r.get('method','')[:8]:8} {r.get('uri','')}")

    print(f"\nGame routes ({len(game_routes)}):")
    for r in game_routes[:20]:
        print(f"  {r.get('method','')[:8]:8} {r.get('uri','')}")

    print(f"\nAuth routes ({len(auth_routes)}):")
    for r in auth_routes[:10]:
        print(f"  {r.get('method','')[:8]:8} {r.get('uri','')}")

except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print("Raw:", out[:500])
    routes_data = []

# Step 3: Check controller authorization code
print("\n=== Checking Controllers ===")

for ctrl_name in ['PostController', 'JobController', 'GameController', 'MarketController']:
    out_find, _ = run(f"find {project_root}/app -name '{ctrl_name}.php' 2>/dev/null")
    ctrl_path = out_find.strip()
    if ctrl_path:
        content, _ = run(f"cat '{ctrl_path}'")
        print(f"\n### {ctrl_name} ({ctrl_path}) ###")
        print(content[:6000])
    else:
        print(f"\n{ctrl_name}: NOT FOUND")

# PointController
out, _ = run(f"find {project_root}/app -name '*Point*' 2>/dev/null | head -10")
print(f"\nPoint-related files: {out}")
for pt in [p.strip() for p in out.strip().split('\n') if p.strip() and p.endswith('.php')]:
    content, _ = run(f"cat '{pt}'")
    print(f"\n### {pt} ###")
    print(content[:5000])

# Check migrations for points
print("\n=== Points in migrations ===")
out, _ = run(f"grep -rl 'points' {project_root}/database/migrations/ 2>/dev/null | head -10")
for mig in [m.strip() for m in out.strip().split('\n') if m.strip()]:
    content, _ = run(f"cat '{mig}'")
    print(f"\n{mig}:")
    print(content[:2000])

# User model
out, _ = run(f"find {project_root}/app -name 'User.php' 2>/dev/null | head -2")
user_model = out.strip().split('\n')[0] if out.strip() else ''
if user_model:
    content, _ = run(f"cat '{user_model}'")
    print(f"\n### User model ###")
    print(content[:4000])

# API routes file
print("\n=== API Routes file ===")
out, _ = run(f"cat {project_root}/routes/api.php 2>/dev/null", timeout=30)
print(out[:15000])

# All controllers list
print("\n=== All Controllers ===")
out, _ = run(f"ls {project_root}/app/Http/Controllers/ 2>/dev/null")
print(out)

# Step 4: Create test users
print("\n\n=== Creating 20 Test Users ===")

php_create = r"""<?php
require __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

use App\Models\User;
use Illuminate\Support\Facades\Hash;

$users_to_create = [
    ['username' => 'testadmin1', 'email' => 'testadmin1@test.com', 'name' => 'Test Admin 1', 'category' => 'admin_tester'],
    ['username' => 'testadmin2', 'email' => 'testadmin2@test.com', 'name' => 'Test Admin 2', 'category' => 'admin_tester'],
    ['username' => 'user01', 'email' => 'user01@test.com', 'name' => 'User 01', 'category' => 'general'],
    ['username' => 'user02', 'email' => 'user02@test.com', 'name' => 'User 02', 'category' => 'general'],
    ['username' => 'user03', 'email' => 'user03@test.com', 'name' => 'User 03', 'category' => 'general'],
    ['username' => 'user04', 'email' => 'user04@test.com', 'name' => 'User 04', 'category' => 'general'],
    ['username' => 'user05', 'email' => 'user05@test.com', 'name' => 'User 05', 'category' => 'general'],
    ['username' => 'user06', 'email' => 'user06@test.com', 'name' => 'User 06', 'category' => 'general'],
    ['username' => 'user07', 'email' => 'user07@test.com', 'name' => 'User 07', 'category' => 'general'],
    ['username' => 'user08', 'email' => 'user08@test.com', 'name' => 'User 08', 'category' => 'general'],
    ['username' => 'user09', 'email' => 'user09@test.com', 'name' => 'User 09', 'category' => 'general'],
    ['username' => 'user10', 'email' => 'user10@test.com', 'name' => 'User 10', 'category' => 'general'],
    ['username' => 'oper01', 'email' => 'oper01@test.com', 'name' => 'Operator 01', 'category' => 'operator'],
    ['username' => 'oper02', 'email' => 'oper02@test.com', 'name' => 'Operator 02', 'category' => 'operator'],
    ['username' => 'oper03', 'email' => 'oper03@test.com', 'name' => 'Operator 03', 'category' => 'operator'],
    ['username' => 'points01', 'email' => 'points01@test.com', 'name' => 'Points 01', 'category' => 'points_analyst'],
    ['username' => 'points02', 'email' => 'points02@test.com', 'name' => 'Points 02', 'category' => 'points_analyst'],
    ['username' => 'points03', 'email' => 'points03@test.com', 'name' => 'Points 03', 'category' => 'points_analyst'],
    ['username' => 'points04', 'email' => 'points04@test.com', 'name' => 'Points 04', 'category' => 'points_analyst'],
    ['username' => 'points05', 'email' => 'points05@test.com', 'name' => 'Points 05', 'category' => 'points_analyst'],
];

$results = [];
$password = 'Test1234!';
$fillable = (new User())->getFillable();
echo "Fillable fields: " . implode(', ', $fillable) . "\n";

foreach ($users_to_create as $u) {
    try {
        // Delete existing
        $existing = User::where('email', $u['email'])->orWhere(function($q) use ($u, $fillable) {
            if (in_array('username', $fillable)) $q->orWhere('username', $u['username']);
            if (in_array('nickname', $fillable)) $q->orWhere('nickname', $u['username']);
        })->first();
        if ($existing) {
            if (method_exists($existing, 'tokens')) $existing->tokens()->delete();
            $existing->forceDelete();
        }

        $userData = ['email' => $u['email'], 'password' => Hash::make($password)];
        if (in_array('username', $fillable)) $userData['username'] = $u['username'];
        if (in_array('name', $fillable)) $userData['name'] = $u['name'];
        if (in_array('nickname', $fillable)) $userData['nickname'] = $u['username'];
        if (in_array('email_verified_at', $fillable)) $userData['email_verified_at'] = now();

        $user = User::create($userData);
        // Force email verification if column exists
        try {
            $user->email_verified_at = now();
            $user->save();
        } catch(\Exception $e2) {}

        $token = null;
        if (method_exists($user, 'createToken')) {
            $tokenResult = $user->createToken('test-token');
            $token = $tokenResult->plainTextToken ?? null;
            if (!$token && isset($tokenResult->accessToken)) {
                $token = $tokenResult->accessToken;
            }
        }

        $results[] = [
            'username' => $u['username'],
            'email' => $u['email'],
            'password' => $password,
            'category' => $u['category'],
            'id' => $user->id,
            'token' => $token,
            'status' => 'created'
        ];
        echo "Created: {$u['username']} (id={$user->id})\n";
    } catch (\Exception $e) {
        $results[] = [
            'username' => $u['username'],
            'email' => $u['email'],
            'category' => $u['category'],
            'status' => 'error',
            'error' => $e->getMessage()
        ];
        echo "Error {$u['username']}: " . $e->getMessage() . "\n";
    }
}

file_put_contents('/tmp/test_users.json', json_encode($results));
echo "\nJSON_OUTPUT_START\n";
echo json_encode($results, JSON_PRETTY_PRINT);
echo "\nJSON_OUTPUT_END\n";
"""

write_file(f'{project_root}/ct_create_users.php', php_create)
out, err = run(f"cd {project_root} && php ct_create_users.php 2>&1", timeout=120)
print(out[:6000])
if err:
    print("STDERR:", err[:1000])

users = []
if 'JSON_OUTPUT_START' in out and 'JSON_OUTPUT_END' in out:
    json_str = out.split('JSON_OUTPUT_START\n')[1].split('\nJSON_OUTPUT_END')[0]
    try:
        users = json.loads(json_str)
        print(f"\nParsed {len(users)} users")
    except Exception as e:
        print(f"Parse error: {e}")

# Save
write_file('/tmp/test_users.json', json.dumps(users, indent=2))

# Step 5: Run API Tests
print("\n\n=== Running API Tests ===")

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
        CURLOPT_URL => 'http://localhost' . $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 20,
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
    if (!$body && $resp) $body = substr($resp, 0, 300);
    return ['status' => $code, 'body' => $body];
}

function test($label, $method, $url, $token, $data, $expected, &$results, $extra = []) {
    global $results;
    $r = api($method, $url, $token, $data);
    $status = $r['status'];
    $expected_arr = is_array($expected) ? $expected : [$expected];

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

    $body_str = is_array($r['body']) ? json_encode($r['body']) : (string)$r['body'];
    echo "[$pass] $label => HTTP $status (expected " . implode('/', $expected_arr) . ")\n";
    if ($pass === 'FAIL' || $pass === 'SERVER_ERROR') {
        echo "  Body: " . substr($body_str, 0, 200) . "\n";
    }

    $entry = array_merge([
        'label' => $label,
        'method' => $method,
        'endpoint' => $url,
        'status' => $status,
        'pass' => $pass,
        'expected' => $expected,
        'body_preview' => substr($body_str, 0, 300),
    ], $extra);
    $results[] = $entry;
    return $r;
}

// Load users
$users = json_decode(file_get_contents('/tmp/test_users.json'), true);
$tokens = [];
$ids = [];
foreach ($users as $u) {
    if ($u['status'] === 'created' && !empty($u['token'])) {
        $tokens[$u['username']] = $u['token'];
        $ids[$u['username']] = $u['id'];
    }
}
echo "Loaded " . count($tokens) . " user tokens: " . implode(', ', array_keys($tokens)) . "\n\n";

// Try API login to refresh tokens
function try_login($email, $password) {
    $r = api('POST', '/api/login', null, ['email' => $email, 'password' => $password]);
    if ($r['status'] === 200 && is_array($r['body'])) {
        return $r['body']['token'] ?? $r['body']['access_token'] ??
               ($r['body']['data']['token'] ?? null);
    }
    // Also try /api/auth/login
    $r2 = api('POST', '/api/auth/login', null, ['email' => $email, 'password' => $password]);
    if ($r2['status'] === 200 && is_array($r2['body'])) {
        return $r2['body']['token'] ?? $r2['body']['access_token'] ??
               ($r2['body']['data']['token'] ?? null);
    }
    return null;
}

// Refresh tokens via login
$password = 'Test1234!';
foreach ($users as $u) {
    if ($u['status'] !== 'created') continue;
    $fresh = try_login($u['email'], $password);
    if ($fresh) {
        $tokens[$u['username']] = $fresh;
        echo "Refreshed token for {$u['username']}\n";
    }
}
echo "\n";

// ========================
// SECTION 1: ADMIN TESTS
// ========================
echo "=== ADMIN ACCESS TESTS ===\n";
foreach (['testadmin1', 'testadmin2'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }

    test("[$u] GET /api/admin/stats", 'GET', '/api/admin/stats', $tok, [], [401,403], $results, ['category'=>'admin_tester','user'=>$u]);
    test("[$u] GET /api/admin/members", 'GET', '/api/admin/members', $tok, [], [401,403], $results, ['category'=>'admin_tester','user'=>$u]);
    test("[$u] GET /api/admin/users", 'GET', '/api/admin/users', $tok, [], [401,403], $results, ['category'=>'admin_tester','user'=>$u]);
    test("[$u] GET /api/admin/dashboard", 'GET', '/api/admin/dashboard', $tok, [], [401,403], $results, ['category'=>'admin_tester','user'=>$u]);
    test("[$u] GET /api/admin/posts", 'GET', '/api/admin/posts', $tok, [], [401,403], $results, ['category'=>'admin_tester','user'=>$u]);
    test("[$u] GET /api/admin/jobs", 'GET', '/api/admin/jobs', $tok, [], [401,403], $results, ['category'=>'admin_tester','user'=>$u]);
}

// ========================
// SECTION 2: GENERAL USER TESTS
// ========================
echo "\n=== GENERAL USER TESTS ===\n";
$created_posts = [];
$created_jobs = [];
$created_markets = [];

foreach (['user01','user02','user03'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }
    $uid = $ids[$u] ?? 1;

    // Profile
    $r = test("[$u] GET /api/user (own profile)", 'GET', '/api/user', $tok, [], [200], $results, ['category'=>'general_user','user'=>$u]);
    if ($r['status'] === 200 && is_array($r['body'])) {
        $points = $r['body']['points'] ?? $r['body']['data']['points'] ?? 'N/A';
        echo "  Points for $u: $points\n";
    }

    // Create post
    $r = api('POST', '/api/posts', $tok, [
        'title' => "Test post by $u",
        'content' => "Content by $u - testing platform",
        'category' => 'general',
        'board_type' => 'general',
    ]);
    $post_id = null;
    if ($r['status'] === 200 || $r['status'] === 201) {
        $b = $r['body'];
        $post_id = is_array($b) ? ($b['id'] ?? $b['data']['id'] ?? $b['post']['id'] ?? null) : null;
        $created_posts[$u] = $post_id;
    }
    $results[] = ['label'=>"[$u] POST /api/posts",'method'=>'POST','endpoint'=>'/api/posts','status'=>$r['status'],'pass'=>in_array($r['status'],[200,201])?'PASS':'FAIL','expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$post_id,'body_preview'=>substr(json_encode($r['body']),0,300)];
    echo "[" . (in_array($r['status'],[200,201])?'PASS':'FAIL') . "] [$u] POST /api/posts => HTTP {$r['status']} post_id=$post_id\n";

    // Create comment
    if ($post_id) {
        $r = api('POST', "/api/posts/{$post_id}/comments", $tok, ['content' => "Comment by $u"]);
        if ($r['status'] === 404) {
            $r = api('POST', '/api/comments', $tok, ['post_id' => $post_id, 'content' => "Comment by $u"]);
            $ep = '/api/comments';
        } else {
            $ep = "/api/posts/{$post_id}/comments";
        }
        $pass = in_array($r['status'],[200,201]) ? 'PASS' : 'FAIL';
        echo "[$pass] [$u] POST comment on post $post_id => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] POST comment",'method'=>'POST','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,300)];
    }

    // Create job
    $r = api('POST', '/api/jobs', $tok, [
        'title' => "Job by $u",
        'description' => "Job description by $u",
        'company' => 'Test Corp',
        'location' => 'New York, NY',
        'job_type' => 'full_time',
        'salary' => '60000',
        'contact_email' => "$u@test.com",
        'category' => 'general',
    ]);
    $job_id = null;
    if ($r['status'] === 200 || $r['status'] === 201) {
        $b = $r['body'];
        $job_id = is_array($b) ? ($b['id'] ?? $b['data']['id'] ?? $b['job']['id'] ?? null) : null;
        $created_jobs[$u] = $job_id;
    }
    $pass = in_array($r['status'],[200,201]) ? 'PASS' : 'FAIL';
    echo "[$pass] [$u] POST /api/jobs => HTTP {$r['status']} job_id=$job_id\n";
    $results[] = ['label'=>"[$u] POST /api/jobs",'method'=>'POST','endpoint'=>'/api/jobs','status'=>$r['status'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$job_id,'body_preview'=>substr(json_encode($r['body']),0,300)];

    // Create market listing
    $r = api('POST', '/api/market', $tok, [
        'title' => "Market item by $u",
        'description' => "Market desc by $u",
        'price' => 100,
        'category' => 'electronics',
        'condition' => 'used',
        'location' => 'New York',
    ]);
    $market_id = null;
    if ($r['status'] === 200 || $r['status'] === 201) {
        $b = $r['body'];
        $market_id = is_array($b) ? ($b['id'] ?? $b['data']['id'] ?? null) : null;
        $created_markets[$u] = $market_id;
    }
    $pass = in_array($r['status'],[200,201]) ? 'PASS' : 'FAIL';
    echo "[$pass] [$u] POST /api/market => HTTP {$r['status']} market_id=$market_id\n";
    $results[] = ['label'=>"[$u] POST /api/market",'method'=>'POST','endpoint'=>'/api/market','status'=>$r['status'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$market_id,'body_preview'=>substr(json_encode($r['body']),0,300)];

    // Check points
    foreach (['/api/points', '/api/user/points', "/api/users/{$uid}/points"] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status'] === 200 ? 'PASS' : ($r['status'] === 404 ? 'N/A_404' : 'INFO');
        echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'points_check','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,300)];
    }

    // Check game endpoints
    foreach (['/api/games', '/api/game', '/api/games/list', '/api/mini-games'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status'] === 200 ? 'PASS' : ($r['status'] === 404 ? 'N/A_404' : 'INFO');
        echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'game_check','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,300)];
    }
}

// ========================
// SECTION 3: CROSS-USER AUTHORIZATION
// ========================
echo "\n=== CROSS-USER AUTHORIZATION TESTS ===\n";

// user02 tries to edit user01's post
if (!empty($created_posts['user01']) && !empty($tokens['user02'])) {
    $pid = $created_posts['user01'];
    $tok2 = $tokens['user02'];

    $r = api('PUT', "/api/posts/{$pid}", $tok2, ['title'=>'HACKED','content'=>'HACKED by user02']);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] user02 PUT /api/posts/{$pid} (user01 post) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"user02 edits user01 post",'method'=>'PUT','endpoint'=>"/api/posts/{$pid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'cross_user_auth','user'=>'user02 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];

    $r = api('PATCH', "/api/posts/{$pid}", $tok2, ['title'=>'HACKED']);
    $pass = in_array($r['status'],[401,403,405]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] user02 PATCH /api/posts/{$pid} => HTTP {$r['status']}\n";
    $results[] = ['label'=>"user02 PATCH user01 post",'method'=>'PATCH','endpoint'=>"/api/posts/{$pid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403,405],'category'=>'cross_user_auth','user'=>'user02 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];

    $r = api('DELETE', "/api/posts/{$pid}", $tok2, []);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] user02 DELETE /api/posts/{$pid} (user01 post) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"user02 deletes user01 post",'method'=>'DELETE','endpoint'=>"/api/posts/{$pid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'cross_user_auth','user'=>'user02 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];
}

// user02 tries to edit user01's job
if (!empty($created_jobs['user01']) && !empty($tokens['user02'])) {
    $jid = $created_jobs['user01'];
    $tok2 = $tokens['user02'];

    $r = api('PUT', "/api/jobs/{$jid}", $tok2, ['title'=>'HACKED job']);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] user02 PUT /api/jobs/{$jid} (user01 job) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"user02 edits user01 job",'method'=>'PUT','endpoint'=>"/api/jobs/{$jid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'cross_user_auth','user'=>'user02 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];

    $r = api('DELETE', "/api/jobs/{$jid}", $tok2, []);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] user02 DELETE /api/jobs/{$jid} (user01 job) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"user02 deletes user01 job",'method'=>'DELETE','endpoint'=>"/api/jobs/{$jid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'cross_user_auth','user'=>'user02 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];
}

// Also test: testadmin1 tries to edit user01's post
if (!empty($created_posts['user01']) && !empty($tokens['testadmin1'])) {
    $pid = $created_posts['user01'];
    $tok_adm = $tokens['testadmin1'];

    $r = api('PUT', "/api/posts/{$pid}", $tok_adm, ['title'=>'Admin hacked']);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] testadmin1 PUT /api/posts/{$pid} (user01 post) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"testadmin1 edits user01 post",'method'=>'PUT','endpoint'=>"/api/posts/{$pid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'admin_tester','user'=>'testadmin1 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];

    $r = api('DELETE', "/api/posts/{$pid}", $tok_adm, []);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] testadmin1 DELETE /api/posts/{$pid} (user01 post) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"testadmin1 deletes user01 post",'method'=>'DELETE','endpoint'=>"/api/posts/{$pid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'admin_tester','user'=>'testadmin1 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];
}

// testadmin2 tries to edit user01's job
if (!empty($created_jobs['user01']) && !empty($tokens['testadmin2'])) {
    $jid = $created_jobs['user01'];
    $tok_adm = $tokens['testadmin2'];

    $r = api('PUT', "/api/jobs/{$jid}", $tok_adm, ['title'=>'Admin hacked job']);
    $pass = in_array($r['status'],[401,403]) ? 'PASS' : ($r['status']===404?'N/A_404':'FAIL_SECURITY_BUG');
    echo "[$pass] testadmin2 PUT /api/jobs/{$jid} (user01 job) => HTTP {$r['status']}\n";
    $results[] = ['label'=>"testadmin2 edits user01 job",'method'=>'PUT','endpoint'=>"/api/jobs/{$jid}",'status'=>$r['status'],'pass'=>$pass,'expected'=>[401,403],'category'=>'admin_tester','user'=>'testadmin2 vs user01','security_risk'=>$r['status']===200?'HIGH':'none','body_preview'=>substr(json_encode($r['body']),0,300)];
}

// ========================
// SECTION 4: OPERATOR TESTS
// ========================
echo "\n=== OPERATOR TESTS ===\n";
foreach (['oper01','oper02'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }

    foreach (['/api/moderator', '/api/moderator/posts', '/api/reports', '/api/admin/moderate', '/api/content/moderate'] as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'operator_test','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,200)];
    }
    // Also do regular user actions
    $r = api('GET', '/api/user', $tok);
    $pass = $r['status']===200 ? 'PASS' : 'FAIL';
    echo "[$pass] [$u] GET /api/user => HTTP {$r['status']}\n";
    $results[] = ['label'=>"[$u] GET /api/user",'method'=>'GET','endpoint'=>'/api/user','status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'operator_test','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,200)];
}

// ========================
// SECTION 5: POINTS ANALYST TESTS
// ========================
echo "\n=== POINTS ANALYST TESTS ===\n";
foreach (['points01','points02'] as $u) {
    $tok = $tokens[$u] ?? null;
    if (!$tok) { echo "No token for $u\n"; continue; }
    $uid = $ids[$u] ?? 1;

    // Profile with points check
    $r = api('GET', '/api/user', $tok);
    $pass = $r['status']===200 ? 'PASS' : 'FAIL';
    $pts = null;
    if ($r['status']===200 && is_array($r['body'])) {
        $pts = $r['body']['points'] ?? $r['body']['data']['points'] ?? 'field_not_found';
    }
    echo "[$pass] [$u] GET /api/user => HTTP {$r['status']} | points=$pts\n";
    $results[] = ['label'=>"[$u] GET /api/user (check points)",'method'=>'GET','endpoint'=>'/api/user','status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'points_analyst','user'=>$u,'points_value'=>$pts,'body_preview'=>substr(json_encode($r['body']),0,400)];

    // All points endpoints
    $pts_endpoints = [
        '/api/points',
        '/api/user/points',
        "/api/users/{$uid}/points",
        '/api/point-history',
        '/api/points/history',
        '/api/points/transactions',
        '/api/transactions',
        '/api/points/balance',
        '/api/wallet',
        '/api/leaderboard',
        '/api/rankings',
        '/api/points/earn',
    ];
    foreach ($pts_endpoints as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        if ($r['status'] !== 404) {
            echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
            $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'points_analyst','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400)];
        }
    }

    // Game endpoints
    $game_endpoints = [
        '/api/games',
        '/api/games/list',
        '/api/game',
        '/api/mini-games',
        '/api/games/bet',
        '/api/game/create',
        '/api/games/create',
        '/api/holdem',
        '/api/game/holdem',
    ];
    foreach ($game_endpoints as $ep) {
        $r = api('GET', $ep, $tok);
        $pass = $r['status']===200 ? 'PASS' : ($r['status']===404?'N/A_404':'INFO');
        if ($r['status'] !== 404) {
            echo "[$pass] [$u] GET $ep => HTTP {$r['status']}\n";
            $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$r['status'],'pass'=>$pass,'expected'=>[200],'category'=>'game_test','user'=>$u,'body_preview'=>substr(json_encode($r['body']),0,400)];
        }
    }

    // Test if posting awards points
    $r_before = api('GET', '/api/user', $tok);
    $pts_before = null;
    if ($r_before['status']===200 && is_array($r_before['body'])) {
        $pts_before = $r_before['body']['points'] ?? $r_before['body']['data']['points'] ?? null;
    }

    $r_post = api('POST', '/api/posts', $tok, [
        'title' => "Points test post by $u",
        'content' => "Testing if creating post awards points",
        'category' => 'general',
    ]);

    $r_after = api('GET', '/api/user', $tok);
    $pts_after = null;
    if ($r_after['status']===200 && is_array($r_after['body'])) {
        $pts_after = $r_after['body']['points'] ?? $r_after['body']['data']['points'] ?? null;
    }

    echo "[$u] Points before post: $pts_before, after post: $pts_after (post_status={$r_post['status']})\n";
    $results[] = [
        'label' => "[$u] points awarded for post",
        'category' => 'points_award_test',
        'user' => $u,
        'points_before' => $pts_before,
        'points_after' => $pts_after,
        'points_changed' => ($pts_before !== null && $pts_after !== null && $pts_before !== $pts_after),
        'post_status' => $r_post['status'],
        'pass' => 'INFO',
        'status' => $r_post['status'],
        'endpoint' => '/api/posts',
        'expected' => 'info',
        'body_preview' => ''
    ];
}

// ========================
// FINAL SUMMARY
// ========================
echo "\n=== FINAL SUMMARY ===\n";
$total = count($results);
$passed = count(array_filter($results, fn($r) => $r['pass'] === 'PASS'));
$failed = count(array_filter($results, fn($r) => $r['pass'] === 'FAIL' || $r['pass'] === 'FAIL_SECURITY_BUG'));
$server_errors = count(array_filter($results, fn($r) => $r['pass'] === 'SERVER_ERROR'));
$na = count(array_filter($results, fn($r) => $r['pass'] === 'N/A_404'));

echo "Total tests: $total\n";
echo "PASSED: $passed\n";
echo "FAILED: $failed\n";
echo "SERVER ERRORS: $server_errors\n";
echo "N/A (404): $na\n";

echo "\n--- Security Issues ---\n";
$sec = array_filter($results, fn($r) => ($r['security_risk'] ?? 'none') !== 'none');
foreach ($sec as $s) {
    echo "SECURITY: {$s['method']} {$s['endpoint']} => HTTP {$s['status']} | {$s['security_risk']}\n";
}
if (empty($sec)) echo "None found\n";

echo "\n--- Server Errors ---\n";
$errs = array_filter($results, fn($r) => $r['pass'] === 'SERVER_ERROR');
foreach ($errs as $e) {
    echo "500: {$e['method']} {$e['endpoint']}\n";
    echo "  Body: " . substr($e['body_preview'], 0, 300) . "\n";
}
if (empty($errs)) echo "None found\n";

echo "\n--- Failed Tests (unexpected) ---\n";
$fails = array_filter($results, fn($r) => $r['pass'] === 'FAIL' || $r['pass'] === 'FAIL_SECURITY_BUG');
foreach ($fails as $f) {
    echo "FAIL: {$f['label']} => HTTP {$f['status']} (expected {$f['expected']})\n";
    echo "  Body: " . substr($f['body_preview'], 0, 200) . "\n";
}
if (empty($fails)) echo "None found\n";

file_put_contents('/tmp/ct_test_results.json', json_encode($results, JSON_PRETTY_PRINT));
echo "\nSaved to /tmp/ct_test_results.json\n";
echo "\nRESULTS_START\n";
echo json_encode($results);
echo "\nRESULTS_END\n";
"""

write_file(f'{project_root}/ct_api_tests.php', php_tests)
print("Running API tests (this may take a few minutes)...")

out_test, err_test = run(f"cd {project_root} && php ct_api_tests.php 2>&1", timeout=300)
print("\n=== API TEST OUTPUT ===")
print(out_test[:20000])
if err_test:
    print("STDERR:", err_test[:2000])

# Parse results
test_results = []
if 'RESULTS_START' in out_test and 'RESULTS_END' in out_test:
    json_section = out_test.split('RESULTS_START\n')[1].split('\nRESULTS_END')[0]
    try:
        test_results = json.loads(json_section)
        print(f"\nParsed {len(test_results)} test results")
    except Exception as e:
        print(f"Parse error: {e}")
        print("JSON preview:", json_section[:500])

# Cleanup
run(f"rm -f {project_root}/ct_create_users.php {project_root}/ct_api_tests.php")

# Build final report
security_bugs = [r for r in test_results if r.get('security_risk','none') != 'none' or r.get('pass','') == 'FAIL_SECURITY_BUG']
server_errs = [r for r in test_results if r.get('pass') == 'SERVER_ERROR' or r.get('status',0) >= 500]
missing_features = [r for r in test_results if r.get('pass') == 'N/A_404']
real_fails = [r for r in test_results if r.get('pass') in ['FAIL', 'FAIL_SECURITY_BUG']]

print("\n\n" + "="*60)
print("COMPREHENSIVE TEST REPORT SUMMARY")
print("="*60)
print(f"\nUsers Created: {len([u for u in users if u.get('status') == 'created'])}/20")
print(f"Total Tests Run: {len(test_results)}")
print(f"PASSED: {len([r for r in test_results if r.get('pass') == 'PASS'])}")
print(f"FAILED: {len(real_fails)}")
print(f"SERVER ERRORS (5xx): {len(server_errs)}")
print(f"N/A (404 not found): {len(missing_features)}")
print(f"SECURITY BUGS: {len(security_bugs)}")

print("\n--- Users Created ---")
for u in users:
    cat = u.get('category','')
    status = u.get('status','')
    token_short = (u.get('token') or '')[:20] + '...' if u.get('token') else 'NO TOKEN'
    print(f"  [{cat:15}] {u.get('username',''):12} | {u.get('email',''):25} | pass=Test1234! | id={u.get('id','?')} | token={token_short} | {status}")

if security_bugs:
    print("\n--- SECURITY BUGS ---")
    for b in security_bugs:
        print(f"  !! {b.get('method')} {b.get('endpoint')} => HTTP {b.get('status')} (expected {b.get('expected')})")
        if b.get('security_risk','none') != 'none':
            print(f"     RISK: {b.get('security_risk')}")

if server_errs:
    print("\n--- SERVER ERRORS ---")
    for e in server_errs:
        print(f"  500: {e.get('method')} {e.get('endpoint')}")
        print(f"     Body: {e.get('body_preview','')[:200]}")

if real_fails:
    print("\n--- FAILED TESTS ---")
    for f in real_fails:
        print(f"  FAIL: {f.get('label')} => HTTP {f.get('status')} (expected {f.get('expected')})")
        print(f"     Body: {f.get('body_preview','')[:200]}")

# Save comprehensive final report
final_report = {
    'summary': {
        'users_created': len([u for u in users if u.get('status') == 'created']),
        'total_tests': len(test_results),
        'passed': len([r for r in test_results if r.get('pass') == 'PASS']),
        'failed': len(real_fails),
        'server_errors': len(server_errs),
        'security_bugs': len(security_bugs),
        'missing_features_404': len(missing_features),
    },
    'users': users,
    'test_results': test_results,
    'security_bugs': security_bugs,
    'server_errors': server_errs,
    'failed_tests': real_fails,
    'missing_features': [r.get('endpoint') for r in missing_features],
}

with open('C:/Users/Admin/Desktop/somekorean/comprehensive_test_report.json', 'w', encoding='utf-8') as f:
    json.dump(final_report, f, indent=2, ensure_ascii=False)

print("\nReport saved to comprehensive_test_report.json")
ssh.close()
print("SSH connection closed.")
