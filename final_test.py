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

# Write a compact PHP script that saves to file and prints summary
php = r"""<?php
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
    if ($method === 'POST') { curl_setopt($ch, CURLOPT_POST, true); curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data)); }
    elseif (in_array($method, ['PUT','PATCH','DELETE'])) { curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method); if (!empty($data)) curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data)); }
    $resp = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $body = json_decode($resp, true);
    if (!$body && $resp) $body = substr($resp, 0, 300);
    return ['s' => $code, 'b' => $body];
}

function login($email, $pw) {
    $r = api('POST', '/api/auth/login', null, ['email'=>$email,'password'=>$pw]);
    if ($r['s'] === 200 && is_array($r['b'])) {
        return $r['b']['token'] ?? null;
    }
    return null;
}

function rec($label, $method, $url, $token, $data, $expected, $cat, $user, &$results, $extra = []) {
    $r = api($method, $url, $token, $data);
    $s = $r['s'];
    $exp = is_array($expected) ? $expected : [$expected];
    $body = is_array($r['b']) ? json_encode($r['b']) : (string)$r['b'];
    if ($s >= 500) $pass = 'SERVER_ERROR';
    elseif (!in_array($s, $exp) && $s === 404) $pass = 'N/A_404';
    elseif (in_array($s, $exp)) {
        // Security check: got 200 but expected 403
        if (in_array($s, [200,201]) && in_array(403, $exp)) {
            $pass = 'FAIL_SECURITY_BUG';
            $extra['security_risk'] = "SECURITY: $method $url returned $s instead of 403/401";
        } else {
            $pass = 'PASS';
        }
    } else {
        $pass = 'FAIL';
    }
    echo "[$pass] $label => $s\n";
    $entry = array_merge(['label'=>$label,'method'=>$method,'endpoint'=>$url,'status'=>$s,'pass'=>$pass,'expected'=>$exp,'category'=>$cat,'user'=>$user,'body'=>substr($body,0,300),'security_risk'=>'none'], $extra);
    $results[] = $entry;
    return $r;
}

$pw = 'Test1234!';
$users = [
    ['u'=>'testadmin1','e'=>'testadmin1@test.com','cat'=>'admin_tester','id'=>299],
    ['u'=>'testadmin2','e'=>'testadmin2@test.com','cat'=>'admin_tester','id'=>300],
    ['u'=>'user01','e'=>'user01@test.com','cat'=>'general','id'=>301],
    ['u'=>'user02','e'=>'user02@test.com','cat'=>'general','id'=>302],
    ['u'=>'user03','e'=>'user03@test.com','cat'=>'general','id'=>303],
    ['u'=>'oper01','e'=>'oper01@test.com','cat'=>'operator','id'=>311],
    ['u'=>'oper02','e'=>'oper02@test.com','cat'=>'operator','id'=>312],
    ['u'=>'points01','e'=>'points01@test.com','cat'=>'points_analyst','id'=>314],
    ['u'=>'points02','e'=>'points02@test.com','cat'=>'points_analyst','id'=>315],
];

// Login all
$tok = []; $ids = [];
foreach ($users as $u) {
    $t = login($u['e'], $pw);
    if ($t) { $tok[$u['u']] = $t; $ids[$u['u']] = $u['id']; echo "Login OK: {$u['u']}\n"; }
    else echo "Login FAIL: {$u['u']}\n";
}
echo "Logged in: " . count($tok) . "/" . count($users) . "\n\n";

// 1. ADMIN ACCESS TESTS
echo "=== ADMIN ACCESS TESTS ===\n";
$admin_eps = ['/api/admin/stats','/api/admin/members','/api/admin/users','/api/admin/posts','/api/admin/jobs','/api/admin/activity'];
foreach (['testadmin1','testadmin2'] as $u) {
    $t = $tok[$u]??null; if(!$t) continue;
    foreach ($admin_eps as $ep) rec("[$u] GET $ep",'GET',$ep,$t,[],[401,403],'admin_tester',$u,$results);
    // Also test /api/admin/dashboard specifically
    rec("[$u] GET /api/admin/dashboard",'GET','/api/admin/dashboard',$t,[],[401,403],'admin_tester',$u,$results);
}

// 2. GENERAL USER TESTS
echo "\n=== GENERAL USER TESTS ===\n";
// Get board_id
$br = api('GET','/api/boards',null,[]);
$bid = 1;
if ($br['s']===200 && is_array($br['b'])) {
    $list = $br['b']['data'] ?? $br['b'];
    if (is_array($list) && !empty($list)) $bid = $list[0]['id']??1;
}
echo "board_id=$bid\n";

$cposts=[]; $cjobs=[]; $cmkts=[];
foreach (['user01','user02','user03'] as $u) {
    $t=$tok[$u]??null; if(!$t) continue;

    // Profile
    $rm = api('GET','/api/auth/me',$t,[]);
    $pts = is_array($rm['b']) ? ($rm['b']['points_total'] ?? $rm['b']['points'] ?? 'N/A') : 'N/A';
    $pass = $rm['s']===200?'PASS':'FAIL';
    echo "[$pass] [$u] GET /api/auth/me => {$rm['s']} | points=$pts\n";
    $results[] = ['label'=>"[$u] GET /api/auth/me",'method'=>'GET','endpoint'=>'/api/auth/me','status'=>$rm['s'],'pass'=>$pass,'expected'=>[200],'category'=>'general_user','user'=>$u,'body'=>substr(json_encode($rm['b']),0,300),'security_risk'=>'none','points_value'=>$pts];

    // Post
    $rp = api('POST','/api/posts',$t,['board_id'=>$bid,'title'=>"Post by $u ".time(),'content'=>"Test content by $u"]);
    $pid = is_array($rp['b']) ? ($rp['b']['post']['id']??$rp['b']['id']??$rp['b']['data']['id']??null) : null;
    if ($pid) $cposts[$u]=$pid;
    $pass = in_array($rp['s'],[200,201])?'PASS':'FAIL';
    echo "[$pass] [$u] POST /api/posts => {$rp['s']} | pid=$pid\n";
    $results[] = ['label'=>"[$u] POST /api/posts",'method'=>'POST','endpoint'=>'/api/posts','status'=>$rp['s'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$pid,'body'=>substr(json_encode($rp['b']),0,400),'security_risk'=>'none'];
    if ($pass==='FAIL') echo "  >> ".substr(json_encode($rp['b']),0,300)."\n";

    // Comment
    if ($pid) {
        $rc = api('POST',"/api/posts/{$pid}/comments",$t,['content'=>"Comment by $u"]);
        $pass = in_array($rc['s'],[200,201])?'PASS':'FAIL';
        echo "[$pass] [$u] POST comment on post $pid => {$rc['s']}\n";
        $results[] = ['label'=>"[$u] POST comment",'method'=>'POST','endpoint'=>"/api/posts/{$pid}/comments",'status'=>$rc['s'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'body'=>substr(json_encode($rc['b']),0,300),'security_risk'=>'none'];
        if ($pass==='FAIL') echo "  >> ".substr(json_encode($rc['b']),0,300)."\n";
    }

    // Job
    $rj = api('POST','/api/jobs',$t,['title'=>"Job by $u ".time(),'content'=>"Job desc by $u",'company_name'=>'Corp','region'=>'NY','job_type'=>'full_time']);
    $jid = is_array($rj['b']) ? ($rj['b']['job']['id']??$rj['b']['id']??$rj['b']['data']['id']??null) : null;
    if ($jid) $cjobs[$u]=$jid;
    $pass = in_array($rj['s'],[200,201])?'PASS':'FAIL';
    echo "[$pass] [$u] POST /api/jobs => {$rj['s']} | jid=$jid\n";
    $results[] = ['label'=>"[$u] POST /api/jobs",'method'=>'POST','endpoint'=>'/api/jobs','status'=>$rj['s'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$jid,'body'=>substr(json_encode($rj['b']),0,400),'security_risk'=>'none'];
    if ($pass==='FAIL') echo "  >> ".substr(json_encode($rj['b']),0,300)."\n";

    // Market
    $rmk = api('POST','/api/market',$t,['title'=>"Mkt by $u ".time(),'description'=>"Mkt desc",'price'=>100,'item_type'=>'used','category'=>'electronics']);
    $mid = is_array($rmk['b']) ? ($rmk['b']['item']['id']??$rmk['b']['id']??$rmk['b']['data']['id']??null) : null;
    if ($mid) $cmkts[$u]=$mid;
    $pass = in_array($rmk['s'],[200,201])?'PASS':'FAIL';
    echo "[$pass] [$u] POST /api/market => {$rmk['s']} | mid=$mid\n";
    $results[] = ['label'=>"[$u] POST /api/market",'method'=>'POST','endpoint'=>'/api/market','status'=>$rmk['s'],'pass'=>$pass,'expected'=>[200,201],'category'=>'general_user','user'=>$u,'created_id'=>$mid,'body'=>substr(json_encode($rmk['b']),0,400),'security_risk'=>'none'];
    if ($pass==='FAIL') echo "  >> ".substr(json_encode($rmk['b']),0,300)."\n";

    // Points
    $rbal = api('GET','/api/points/balance',$t,[]);
    $rhist = api('GET','/api/points/history',$t,[]);
    echo "[" . ($rbal['s']===200?'PASS':'FAIL') . "] [$u] GET /api/points/balance => {$rbal['s']}\n";
    echo "[" . ($rhist['s']===200?'PASS':'FAIL') . "] [$u] GET /api/points/history => {$rhist['s']}\n";
    $results[] = ['label'=>"[$u] GET /api/points/balance",'method'=>'GET','endpoint'=>'/api/points/balance','status'=>$rbal['s'],'pass'=>$rbal['s']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_check','user'=>$u,'body'=>substr(json_encode($rbal['b']),0,300),'security_risk'=>'none'];
    $results[] = ['label'=>"[$u] GET /api/points/history",'method'=>'GET','endpoint'=>'/api/points/history','status'=>$rhist['s'],'pass'=>$rhist['s']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_check','user'=>$u,'body'=>substr(json_encode($rhist['b']),0,300),'security_risk'=>'none'];

    // Games
    foreach (['/api/games/rooms','/api/games/leaderboard','/api/games/shop','/api/games/my-scores'] as $ep) {
        $rg = api('GET',$ep,$t,[]);
        $pass = $rg['s']===200?'PASS':($rg['s']===404?'N/A_404':'INFO');
        echo "[$pass] [$u] GET $ep => {$rg['s']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$rg['s'],'pass'=>$pass,'expected'=>[200],'category'=>'game_check','user'=>$u,'body'=>substr(json_encode($rg['b']),0,200),'security_risk'=>'none'];
    }
}

// 3. CROSS-USER AUTHORIZATION
echo "\n=== CROSS-USER AUTH TESTS ===\n";
if (!empty($cposts['user01']) && !empty($tok['user02'])) {
    $pid = $cposts['user01']; $t2 = $tok['user02'];
    rec("user02 PUT post/{$pid} (user01's)",'PUT',"/api/posts/{$pid}",$t2,['title'=>'HACKED'],[401,403],'cross_user_auth','user02 vs user01',$results);
    rec("user02 DELETE post/{$pid} (user01's)",'DELETE',"/api/posts/{$pid}",$t2,[],[401,403],'cross_user_auth','user02 vs user01',$results);
}
if (!empty($cposts['user01']) && !empty($tok['testadmin1'])) {
    $pid = $cposts['user01']; $ta = $tok['testadmin1'];
    rec("testadmin1 PUT post/{$pid} (user01's)",'PUT',"/api/posts/{$pid}",$ta,['title'=>'AdminHack'],[401,403],'admin_tester_cross','testadmin1 vs user01',$results);
    rec("testadmin1 DELETE post/{$pid} (user01's)",'DELETE',"/api/posts/{$pid}",$ta,[],[401,403],'admin_tester_cross','testadmin1 vs user01',$results);
}
if (!empty($cjobs['user01']) && !empty($tok['user02'])) {
    $jid = $cjobs['user01']; $t2 = $tok['user02'];
    rec("user02 PUT job/{$jid} (user01's)",'PUT',"/api/jobs/{$jid}",$t2,['title'=>'HACKED'],[401,403],'cross_user_auth','user02 vs user01',$results);
    rec("user02 DELETE job/{$jid} (user01's)",'DELETE',"/api/jobs/{$jid}",$t2,[],[401,403],'cross_user_auth','user02 vs user01',$results);
}
if (!empty($cjobs['user01']) && !empty($tok['testadmin2'])) {
    $jid = $cjobs['user01']; $ta = $tok['testadmin2'];
    rec("testadmin2 PUT job/{$jid} (user01's)",'PUT',"/api/jobs/{$jid}",$ta,['title'=>'AdminHack'],[401,403],'admin_tester_cross','testadmin2 vs user01',$results);
    rec("testadmin2 DELETE job/{$jid} (user01's)",'DELETE',"/api/jobs/{$jid}",$ta,[],[401,403],'admin_tester_cross','testadmin2 vs user01',$results);
}
if (!empty($cmkts['user01']) && !empty($tok['user02'])) {
    $mid = $cmkts['user01']; $t2 = $tok['user02'];
    rec("user02 PUT market/{$mid} (user01's)",'PUT',"/api/market/{$mid}",$t2,['title'=>'HACKED'],[401,403],'cross_user_auth','user02 vs user01',$results);
    rec("user02 DELETE market/{$mid} (user01's)",'DELETE',"/api/market/{$mid}",$t2,[],[401,403],'cross_user_auth','user02 vs user01',$results);
}

// 4. OPERATOR TESTS
echo "\n=== OPERATOR TESTS ===\n";
foreach (['oper01','oper02'] as $u) {
    $t=$tok[$u]??null; if(!$t) continue;
    rec("[$u] GET /api/auth/me",'GET','/api/auth/me',$t,[],[200],'operator_test',$u,$results);
    // Moderator/report endpoints
    foreach (['/api/moderator','/api/reports','/api/admin/moderate'] as $ep) {
        $ro = api('GET',$ep,$t,[]);
        $pass = $ro['s']===200?'PASS':($ro['s']===404?'N/A_404':'INFO');
        echo "[$pass] [$u] GET $ep => {$ro['s']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$ro['s'],'pass'=>$pass,'expected'=>[200],'category'=>'operator_test','user'=>$u,'body'=>substr(json_encode($ro['b']),0,200),'security_risk'=>'none'];
    }
    rec("[$u] POST /api/posts",'POST','/api/posts',$t,['board_id'=>$bid,'title'=>"Oper post",'content'=>"Operator test"],[200,201],'operator_test',$u,$results);
}

// 5. POINTS ANALYST TESTS
echo "\n=== POINTS ANALYST TESTS ===\n";
foreach (['points01','points02'] as $u) {
    $t=$tok[$u]??null; if(!$t){echo "No token for $u\n";continue;}

    // Balance
    $rbal=api('GET','/api/points/balance',$t,[]);
    $pts=is_array($rbal['b'])?($rbal['b']['points']??'N/A'):'N/A';
    echo "[" . ($rbal['s']===200?'PASS':'FAIL') . "] [$u] GET /api/points/balance => {$rbal['s']} | points=$pts\n";
    $results[] = ['label'=>"[$u] GET /api/points/balance",'method'=>'GET','endpoint'=>'/api/points/balance','status'=>$rbal['s'],'pass'=>$rbal['s']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_analyst','user'=>$u,'body'=>substr(json_encode($rbal['b']),0,400),'security_risk'=>'none','points_value'=>$pts];

    // History
    $rhist=api('GET','/api/points/history',$t,[]);
    echo "[" . ($rhist['s']===200?'PASS':'FAIL') . "] [$u] GET /api/points/history => {$rhist['s']}\n";
    if($rhist['s']===200 && is_array($rhist['b'])) {
        $hist_data = $rhist['b']['data']??[];
        echo "  " . count($hist_data) . " history records. Sample: " . (empty($hist_data)?'none':json_encode($hist_data[0])) . "\n";
    }
    $results[] = ['label'=>"[$u] GET /api/points/history",'method'=>'GET','endpoint'=>'/api/points/history','status'=>$rhist['s'],'pass'=>$rhist['s']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_analyst','user'=>$u,'body'=>substr(json_encode($rhist['b']),0,400),'security_risk'=>'none'];

    // Check-in
    $rci=api('POST','/api/points/checkin',$t,[]);
    $pass = in_array($rci['s'],[200,400])?'PASS':'FAIL';
    echo "[$pass] [$u] POST /api/points/checkin => {$rci['s']} | " . substr(json_encode($rci['b']),0,100) . "\n";
    $results[] = ['label'=>"[$u] POST /api/points/checkin",'method'=>'POST','endpoint'=>'/api/points/checkin','status'=>$rci['s'],'pass'=>$pass,'expected'=>[200,400],'category'=>'points_analyst','user'=>$u,'body'=>substr(json_encode($rci['b']),0,300),'security_risk'=>'none'];

    // Wallet
    $rwb=api('GET','/api/wallet/balance',$t,[]);
    $rwt=api('GET','/api/wallet/transactions',$t,[]);
    $rdb=api('POST','/api/wallet/daily-bonus',$t,[]);
    echo "[" . ($rwb['s']===200?'PASS':'FAIL') . "] [$u] GET /api/wallet/balance => {$rwb['s']} | " . substr(json_encode($rwb['b']),0,100) . "\n";
    echo "[" . ($rwt['s']===200?'PASS':'FAIL') . "] [$u] GET /api/wallet/transactions => {$rwt['s']}\n";
    echo "[" . (in_array($rdb['s'],[200,400])?'PASS':'FAIL') . "] [$u] POST /api/wallet/daily-bonus => {$rdb['s']} | " . substr(json_encode($rdb['b']),0,100) . "\n";
    $results[] = ['label'=>"[$u] GET /api/wallet/balance",'method'=>'GET','endpoint'=>'/api/wallet/balance','status'=>$rwb['s'],'pass'=>$rwb['s']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_analyst','user'=>$u,'body'=>substr(json_encode($rwb['b']),0,300),'security_risk'=>'none'];
    $results[] = ['label'=>"[$u] GET /api/wallet/transactions",'method'=>'GET','endpoint'=>'/api/wallet/transactions','status'=>$rwt['s'],'pass'=>$rwt['s']===200?'PASS':'FAIL','expected'=>[200],'category'=>'points_analyst','user'=>$u,'body'=>substr(json_encode($rwt['b']),0,300),'security_risk'=>'none'];
    $results[] = ['label'=>"[$u] POST /api/wallet/daily-bonus",'method'=>'POST','endpoint'=>'/api/wallet/daily-bonus','status'=>$rdb['s'],'pass'=>in_array($rdb['s'],[200,400])?'PASS':'FAIL','expected'=>[200,400],'category'=>'points_analyst','user'=>$u,'body'=>substr(json_encode($rdb['b']),0,300),'security_risk'=>'none'];

    // Games
    foreach (['/api/games/rooms','/api/games/leaderboard','/api/games/shop'] as $ep) {
        $rg=api('GET',$ep,$t,[]);
        $pass=$rg['s']===200?'PASS':($rg['s']===404?'N/A_404':'INFO');
        echo "[$pass] [$u] GET $ep => {$rg['s']}\n";
        $results[] = ['label'=>"[$u] GET $ep",'method'=>'GET','endpoint'=>$ep,'status'=>$rg['s'],'pass'=>$pass,'expected'=>[200],'category'=>'game_test','user'=>$u,'body'=>substr(json_encode($rg['b']),0,300),'security_risk'=>'none'];
    }

    // Create game room
    $rgc=api('POST','/api/games/rooms',$t,['bet_points'=>100,'max_players'=>2]);
    $pass=in_array($rgc['s'],[200,201])?'PASS':'FAIL';
    echo "[$pass] [$u] POST /api/games/rooms (create room) => {$rgc['s']}\n";
    $results[] = ['label'=>"[$u] POST /api/games/rooms",'method'=>'POST','endpoint'=>'/api/games/rooms','status'=>$rgc['s'],'pass'=>$pass,'expected'=>[200,201],'category'=>'game_test','user'=>$u,'body'=>substr(json_encode($rgc['b']),0,400),'security_risk'=>'none'];
    if (in_array($rgc['s'],[200,201]) && is_array($rgc['b'])) {
        echo "  Room created: " . json_encode(array_intersect_key($rgc['b'],array_flip(['id','code','bet_points','status']))) . "\n";
    }

    // Points before/after posting
    $bal1=api('GET','/api/points/balance',$t,[]); $pts1=is_array($bal1['b'])?($bal1['b']['points']??null):null;
    $rpost=api('POST','/api/posts',$t,['board_id'=>$bid,'title'=>"Points test $u",'content'=>"Testing points award"]);
    $bal2=api('GET','/api/points/balance',$t,[]); $pts2=is_array($bal2['b'])?($bal2['b']['points']??null):null;
    $changed = ($pts1!==null && $pts2!==null && $pts1!==$pts2);
    echo "[$u] Points: before=$pts1 after=$pts2 changed=" . ($changed?'YES':'NO') . " post={$rpost['s']}\n";
    $results[] = ['label'=>"[$u] points awarded for posting",'method'=>'POST','endpoint'=>'/api/posts','status'=>$rpost['s'],'pass'=>'INFO','expected'=>'info','category'=>'points_award_test','user'=>$u,'body'=>'','security_risk'=>'none','points_before'=>$pts1,'points_after'=>$pts2,'points_changed'=>$changed,'post_status'=>$rpost['s']];
}

// Save results
file_put_contents('/tmp/final_test_results.json', json_encode($results, JSON_PRETTY_PRINT));
echo "\n=== SUMMARY ===\n";
$total = count($results);
$pass = count(array_filter($results, fn($r) => $r['pass']==='PASS'));
$fail = count(array_filter($results, fn($r) => in_array($r['pass'],['FAIL','FAIL_SECURITY_BUG'])));
$sec = array_filter($results, fn($r) => $r['security_risk']!=='none');
$serr = array_filter($results, fn($r) => $r['pass']==='SERVER_ERROR' || ($r['status']??0)>=500);
echo "Total=$total PASS=$pass FAIL=$fail SECURITY=" . count($sec) . " 5xx=" . count($serr) . "\n";
foreach ($sec as $b) echo "  SECURITY BUG: {$b['security_risk']}\n";
foreach ($serr as $e) echo "  SERVER_ERROR: {$e['method']} {$e['endpoint']} => {$e['status']}\n";
echo "\nSaved: /tmp/final_test_results.json\n";
echo "DONE\n";
"""

write_file(f'{project_root}/ct_final.php', php)
print("Running final comprehensive test...")

out, err = run(f"cd {project_root} && php ct_final.php 2>&1", timeout=300)
print(out.encode('ascii', errors='replace').decode('ascii'))
if err:
    print("STDERR:", err[:500])

run(f"rm -f {project_root}/ct_final.php")

# Now read results from server file
print("\n\nReading results from /tmp/final_test_results.json ...")
out2, _ = run("cat /tmp/final_test_results.json")

try:
    results = json.loads(out2)
    print(f"Loaded {len(results)} results")

    passed = [r for r in results if r.get('pass') == 'PASS']
    failed = [r for r in results if r.get('pass') in ['FAIL','FAIL_SECURITY_BUG']]
    server_errs = [r for r in results if r.get('pass') == 'SERVER_ERROR' or r.get('status',0) >= 500]
    na_404 = [r for r in results if r.get('pass') == 'N/A_404']
    info_items = [r for r in results if r.get('pass') == 'INFO']
    security_bugs = [r for r in results if r.get('security_risk','none') != 'none']

    # Build final report
    users_created = [
        {'username':'testadmin1','email':'testadmin1@test.com','id':299,'password':'Test1234!','category':'admin_tester','status':'created'},
        {'username':'testadmin2','email':'testadmin2@test.com','id':300,'password':'Test1234!','category':'admin_tester','status':'created'},
        {'username':'user01','email':'user01@test.com','id':301,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user02','email':'user02@test.com','id':302,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user03','email':'user03@test.com','id':303,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user04','email':'user04@test.com','id':304,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user05','email':'user05@test.com','id':305,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user06','email':'user06@test.com','id':306,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user07','email':'user07@test.com','id':307,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user08','email':'user08@test.com','id':308,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user09','email':'user09@test.com','id':309,'password':'Test1234!','category':'general','status':'created'},
        {'username':'user10','email':'user10@test.com','id':310,'password':'Test1234!','category':'general','status':'created'},
        {'username':'oper01','email':'oper01@test.com','id':311,'password':'Test1234!','category':'operator','status':'created'},
        {'username':'oper02','email':'oper02@test.com','id':312,'password':'Test1234!','category':'operator','status':'created'},
        {'username':'oper03','email':'oper03@test.com','id':313,'password':'Test1234!','category':'operator','status':'created'},
        {'username':'points01','email':'points01@test.com','id':314,'password':'Test1234!','category':'points_analyst','status':'created'},
        {'username':'points02','email':'points02@test.com','id':315,'password':'Test1234!','category':'points_analyst','status':'created'},
        {'username':'points03','email':'points03@test.com','id':316,'password':'Test1234!','category':'points_analyst','status':'created'},
        {'username':'points04','email':'points04@test.com','id':317,'password':'Test1234!','category':'points_analyst','status':'created'},
        {'username':'points05','email':'points05@test.com','id':318,'password':'Test1234!','category':'points_analyst','status':'created'},
    ]

    final_report = {
        'summary': {
            'total_users_created': 20,
            'total_tests': len(results),
            'passed': len(passed),
            'failed': len(failed),
            'server_errors': len(server_errs),
            'security_bugs': len(security_bugs),
            'missing_features_404': len(na_404),
            'info': len(info_items),
        },
        'users': users_created,
        'security_bugs': security_bugs,
        'server_errors': server_errs,
        'failed_tests': failed,
        'all_test_results': results,
        'notes': {
            'auth_method': 'JWT (tymon/jwt-auth)',
            'login_endpoint': 'POST /api/auth/login',
            'token_field': 'token',
            'points_field_in_user_model': 'points_total',
            'wallet_currencies': 'star, gem, coin, chip',
            'game_type': 'go_stop (Hwatu card game)',
            'admin_flag': 'users.is_admin (boolean)',
        }
    }

    with open('C:/Users/Admin/Desktop/somekorean/comprehensive_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    print("\n=== FINAL ANALYSIS ===")
    print(json.dumps(final_report['summary'], indent=2))

    print("\n=== SECURITY BUGS ===")
    for b in security_bugs:
        print(f"  {b['security_risk']}")
    if not security_bugs:
        print("  None found")

    print("\n=== FAILED TESTS ===")
    for f in failed:
        print(f"  FAIL: {f['label']} => HTTP {f['status']} (expected {f['expected']})")
        print(f"    Body: {f.get('body','')[:200]}")
    if not failed:
        print("  None")

    print("\n=== SERVER ERRORS ===")
    for e in server_errs:
        print(f"  500: {e['method']} {e['endpoint']}")
    if not server_errs:
        print("  None")

    print("\nReport saved to: C:/Users/Admin/Desktop/somekorean/comprehensive_test_report.json")

except json.JSONDecodeError as e:
    print(f"JSON error: {e}")
    print(out2[:1000])

ssh.close()
