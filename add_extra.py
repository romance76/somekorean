#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

php_code = r"""<?php
$pdo = new PDO('mysql:host=localhost;dbname=somekorean;charset=utf8mb4', 'somekorean_user', 'SK_DB@2026!secure');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$admin = 2;
$stmt = $pdo->query("SELECT id FROM users WHERE is_admin=1 LIMIT 1");
$r = $stmt->fetch(); if($r) $admin=$r['id'];

$extras = [
  [6, '녹차 타르트', '집에서 만드는 녹차 타르트, 부드러운 녹차 크림이 매력적이에요.', 'medium', '50분', 320, 4],
  [6, '흑임자 케이크', '고소한 흑임자 향이 가득한 케이크, 특별한 날에 어울려요.', 'hard', '1시간', 380, 6],
  [6, '인절미 토스트', '달콤 고소한 인절미 토스트, 아침 간식으로 딱이에요.', 'easy', '15분', 250, 2],
  [6, '팥 크로플', '바삭한 크로플에 달콤한 팥을 올린 디저트예요.', 'easy', '20분', 290, 2],
  [6, '쑥 라떼', '향긋한 쑥으로 만든 건강 라떼, 따뜻하게 즐겨보세요.', 'easy', '10분', 150, 1],
];

$img = 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600&q=80';
$ingredients = '[{"name":"찹쌀가루","amount":"200g"},{"name":"설탕","amount":"50g"},{"name":"소금","amount":"약간"},{"name":"버터","amount":"30g"}]';
$steps = '[{"step":1,"description":"재료를 계량하여 준비합니다."},{"step":2,"description":"반죽을 만들어 성형합니다."},{"step":3,"description":"오븐에 구워 완성합니다."}]';
$tips = '[{"tip":"신선한 재료를 사용하면 더 맛있어요."}]';
$tags = '["간식","디저트","달콤한"]';

foreach($extras as $e) {
    $exist = $pdo->query("SELECT id FROM recipe_posts WHERE title='".$e[1]."'")->fetch();
    if($exist) { echo "Skip: ".$e[1]."\n"; continue; }
    $days = rand(0,180);
    $created = date('Y-m-d H:i:s', strtotime("-$days days -".rand(0,23)." hours"));
    $pdo->prepare("INSERT INTO recipe_posts (category_id,user_id,title,intro,difficulty,cook_time,calories,servings,ingredients,steps,tips,tags,image_url,image_credit,source,created_at,updated_at,is_hidden,view_count,like_count,bookmark_count) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,?,0,0)")
    ->execute([$e[0],$admin,$e[1],$e[2],$e[3],$e[4],$e[5],$e[6],$ingredients,$steps,$tips,$tags,$img,'Unsplash','system',$created,$created,rand(10,500)]);
    echo "Added: ".$e[1]."\n";
}

// Add likes/comments to new recipes with like_count=0
$users = [];
$s = $pdo->query("SELECT id FROM users");
while($row=$s->fetch()) $users[]=$row['id'];

$comments = [
    "진짜 맛있었어요! 가족들이 너무 좋아했어요 👍",
    "생각보다 어렵지 않네요. 초보도 할 수 있어요!",
    "재료 손질이 좀 걸리지만 결과물은 최고예요",
    "팁 대로 했더니 훨씬 맛있었어요. 감사합니다!",
    "다음엔 치즈 올려서 해볼게요 ㅎㅎ",
    "우리 아이가 엄청 잘 먹었어요. 강추!",
    "만들기 쉽고 맛있어서 자주 해먹을 것 같아요"
];

$new_recipes = $pdo->query("SELECT id,created_at FROM recipe_posts WHERE like_count=0")->fetchAll();
foreach($new_recipes as $nr) {
    $lc = rand(5,47);
    shuffle($users);
    $selected = array_slice($users, 0, min($lc, count($users)));
    foreach($selected as $u) {
        $t = date('Y-m-d H:i:s', strtotime($nr['created_at']) + rand(3600, 86400*30));
        try { $pdo->prepare("INSERT IGNORE INTO recipe_likes (recipe_id,user_id,created_at) VALUES(?,?,?)")->execute([$nr['id'],$u,$t]); } catch(Exception $e) {}
    }
    $cc = rand(2,11);
    for($i=0;$i<$cc;$i++) {
        $u = $users[array_rand($users)];
        $c = $comments[array_rand($comments)];
        $t = date('Y-m-d H:i:s', strtotime($nr['created_at']) + rand(3600, 86400*60));
        $pdo->prepare("INSERT INTO recipe_comments (recipe_id,user_id,content,created_at,updated_at) VALUES(?,?,?,?,?)")->execute([$nr['id'],$u,$c,$t,$t]);
    }
}

$pdo->exec("UPDATE recipe_posts r SET like_count=(SELECT COUNT(*) FROM recipe_likes WHERE recipe_id=r.id)");

echo "\n=== Final Statistics ===\n";
$cat_names = [1=>'한식 메인', 2=>'한식 반찬', 3=>'미국 음식', 4=>'한미 퓨전', 5=>'미국재료로 한식', 6=>'간식/디저트'];
$s = $pdo->query("SELECT category_id, COUNT(*) as cnt FROM recipe_posts GROUP BY category_id ORDER BY category_id");
while($row=$s->fetch()) {
    $name = $cat_names[$row['category_id']] ?? 'Unknown';
    echo "  $name (cat {$row['category_id']}): {$row['cnt']} recipes\n";
}
$s = $pdo->query("SELECT COUNT(*) as t FROM recipe_posts"); echo "\nTotal recipes: ".$s->fetch()['t']."\n";
$s = $pdo->query("SELECT COUNT(*) as t FROM recipe_likes"); echo "Total likes: ".$s->fetch()['t']."\n";
$s = $pdo->query("SELECT COUNT(*) as t FROM recipe_comments"); echo "Total comments: ".$s->fetch()['t']."\n";
$s = $pdo->query("SELECT AVG(like_count) as a FROM recipe_posts"); echo "Avg likes/recipe: ".round($s->fetch()['a'],1)."\n";
$s = $pdo->query("SELECT COUNT(*)/(SELECT COUNT(*) FROM recipe_posts) as a FROM recipe_comments"); echo "Avg comments/recipe: ".round($s->fetch()['a'],1)."\n";
"""

sftp = ssh.open_sftp()
with sftp.file('/var/www/somekorean/gen_extra.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('cd /var/www/somekorean && php gen_extra.php', timeout=120)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err)

ssh.exec_command('rm -f /var/www/somekorean/gen_extra.php')
ssh.close()
print("Done!")
