<?php
set_time_limit(300);
$pdo = new PDO("mysql:host=127.0.0.1;port=3306;dbname=somekorean;charset=utf8mb4","somekorean_user","SK_DB@2026!secure",[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);

echo "=== 작업 1: 깨진 데이터 삭제 ===\n";
$before = $pdo->query("SELECT COUNT(*) FROM shopping_deals")->fetchColumn();
echo "삭제 전 딜 수: {$before}\n";
$pdo->exec("DELETE FROM shopping_deals WHERE original_price IS NULL OR original_price = 0");
$pdo->exec("DELETE FROM shopping_deals WHERE discount_percent IS NULL OR discount_percent <= 0");
$after = $pdo->query("SELECT COUNT(*) FROM shopping_deals")->fetchColumn();
echo "삭제: " . ($before - $after) . "개, 남은 딜: {$after}개\n";

echo "\n=== 작업 2: DB 구조 통합 ===\n";
$cols = $pdo->query("DESCRIBE shopping_stores")->fetchAll(PDO::FETCH_COLUMN);
$additions = [];
if(!in_array('name_en',$cols))        $additions[] = "ADD COLUMN name_en VARCHAR(255) NULL AFTER name";
if(!in_array('chain_name',$cols))     $additions[] = "ADD COLUMN chain_name VARCHAR(50) NULL AFTER name_en";
if(!in_array('category',$cols))       $additions[] = "ADD COLUMN category VARCHAR(30) DEFAULT 'korean_mart' AFTER chain_name";
if(!in_array('logo_url',$cols))       $additions[] = "ADD COLUMN logo_url VARCHAR(500) NULL AFTER category";
if(!in_array('weekly_ad_url',$cols))  $additions[] = "ADD COLUMN weekly_ad_url VARCHAR(500) NULL AFTER website";
if(!in_array('scrape_method',$cols))  $additions[] = "ADD COLUMN scrape_method VARCHAR(20) DEFAULT 'manual' AFTER rss_url";
if(!in_array('scrape_schedule',$cols))$additions[] = "ADD COLUMN scrape_schedule VARCHAR(20) DEFAULT 'manual' AFTER scrape_method";
if(!in_array('memo',$cols))           $additions[] = "ADD COLUMN memo TEXT NULL";
if(!in_array('deleted_at',$cols))     $additions[] = "ADD COLUMN deleted_at TIMESTAMP NULL";
if(!in_array('last_scraped_at',$cols))$additions[] = "ADD COLUMN last_scraped_at TIMESTAMP NULL";
if($additions){
    $pdo->exec("ALTER TABLE shopping_stores " . implode(", ", $additions));
    echo "shopping_stores 컬럼 추가: " . count($additions) . "개\n";
} else echo "shopping_stores 이미 최신\n";

$pdo->exec("UPDATE shopping_stores SET category='korean_mart' WHERE type='korean'");
$pdo->exec("UPDATE shopping_stores SET category='us_mart' WHERE type='american'");
$pdo->exec("UPDATE shopping_stores SET category='asian_mart' WHERE type='asian'");

$pdo->exec("CREATE TABLE IF NOT EXISTS store_locations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    store_id BIGINT UNSIGNED NOT NULL,
    branch_name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NULL, city VARCHAR(100) NULL, state VARCHAR(10) NULL, zip_code VARCHAR(10) NULL,
    lat DECIMAL(10,7) NULL, lng DECIMAL(10,7) NULL,
    phone VARCHAR(30) NULL, open_time VARCHAR(10) DEFAULT '09:00', close_time VARCHAR(10) DEFAULT '21:00',
    open_days JSON NULL, is_24h TINYINT(1) DEFAULT 0, is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP NULL, updated_at TIMESTAMP NULL,
    INDEX idx_store(store_id), INDEX idx_loc(lat,lng)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
echo "store_locations OK\n";

$pdo->exec("CREATE TABLE IF NOT EXISTS store_flyers (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    store_id BIGINT UNSIGNED NOT NULL, title VARCHAR(255) NULL,
    image_url VARCHAR(500) NULL, valid_from DATE NULL, valid_until DATE NULL,
    is_active TINYINT(1) DEFAULT 1, created_at TIMESTAMP NULL, updated_at TIMESTAMP NULL,
    INDEX idx_store(store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
echo "store_flyers OK\n";

$pdo->exec("CREATE TABLE IF NOT EXISTS scrape_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    store_id BIGINT UNSIGNED NOT NULL,
    status VARCHAR(20) DEFAULT 'running', deals_count INT DEFAULT 0,
    error_message TEXT NULL, started_at TIMESTAMP NULL, finished_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL, INDEX idx_store(store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
echo "scrape_logs OK\n";

$dealCols = $pdo->query("DESCRIBE shopping_deals")->fetchAll(PDO::FETCH_COLUMN);
if(!in_array('is_special',$dealCols))
    $pdo->exec("ALTER TABLE shopping_deals ADD COLUMN is_special TINYINT(1) DEFAULT 0 AFTER is_featured");

$userCols = $pdo->query("DESCRIBE users")->fetchAll(PDO::FETCH_COLUMN);
if(!in_array('home_zip_code',$userCols))
    $pdo->exec("ALTER TABLE users ADD COLUMN home_zip_code VARCHAR(10) NULL");

echo "\n=== 작업 3: 마트 데이터 등록 ===\n";

// 기존 데이터 chain_name 매핑
$maps = [
    ['hmart','H Mart','H Mart','%H마트%','%H-Mart%','H Mart%','Super H Mart'],
    ['zion','Zion Market','Zion Market','%Zion%'],
    ['lotte','Lotte Plaza','Lotte Plaza Market','%Lotte%'],
    ['hannam','한남체인','Hannam Chain','%Hannam%'],
    ['costco','Costco','Costco Wholesale','%Costco%'],
    ['kroger','Kroger','Kroger','%Kroger%'],
    ['walmart','Walmart','Walmart','%Walmart%'],
    ['publix','Publix','Publix','%Publix%'],
    ['target','Target','Target','%Target%'],
    ['mitsuwa','Mitsuwa','Mitsuwa Marketplace','%Mitsuwa%'],
    ['99ranch','99 Ranch Market','99 Ranch Market','%99 Ranch%'],
    ['galleria','갤러리아 마켓','Galleria Market','%Galleria%','%KoreaTown%'],
    ['assi','아씨마켓','Assi Market','%Assi%'],
    ['traderjoes','Trader Joes','Trader Joes','%Trader%'],
    ['wholefoods','Whole Foods','Whole Foods Market','%Whole Foods%'],
];
foreach($maps as $m){
    $chain=$m[0]; $name=$m[1]; $nameEn=$m[2];
    $likes = array_slice($m, 3);
    $conds = array_map(fn($l)=>"name LIKE '{$l}'", $likes);
    $where = implode(' OR ', $conds);
    $nameEsc = str_replace("'","''",$name);
    $nameEnEsc = str_replace("'","''",$nameEn);
    $pdo->exec("UPDATE shopping_stores SET chain_name='{$chain}', name='{$nameEsc}', name_en='{$nameEnEsc}' WHERE ({$where}) AND (chain_name IS NULL OR chain_name='')");
}

// 중복 제거
$dupes = $pdo->query("SELECT chain_name, MIN(id) keep_id, GROUP_CONCAT(id) all_ids FROM shopping_stores WHERE chain_name IS NOT NULL AND chain_name!='' GROUP BY chain_name HAVING COUNT(*)>1")->fetchAll(PDO::FETCH_ASSOC);
foreach($dupes as $d){
    foreach(explode(',',$d['all_ids']) as $id){
        if($id != $d['keep_id']){
            $pdo->exec("UPDATE shopping_deals SET store_id={$d['keep_id']} WHERE store_id={$id}");
            $pdo->exec("DELETE FROM shopping_stores WHERE id={$id}");
            echo "  중복 삭제: #{$id} ({$d['chain_name']})\n";
        }
    }
}

// 새 마트 추가
$newStores = [
    ['H Mart','H Mart','hmart','korean_mart','https://hmart.com'],
    ['Zion Market','Zion Market','zion','korean_mart','https://zionmarket.com'],
    ['Lotte Plaza','Lotte Plaza Market','lotte','korean_mart','https://lotteplaza.com'],
    ['한남체인','Hannam Chain','hannam','korean_mart','https://hannamchain.com'],
    ['아씨마켓','Assi Market','assi','korean_mart','https://assimarket.com'],
    ['남대문마트','Namdaemun Market','namdaemun','korean_mart','https://namdaemunmarket.com'],
    ['갤러리아 마켓','Galleria Market','galleria','korean_mart','https://galleriamarket.com'],
    ['한아름','Hanahreum','hanahreum','korean_mart','https://hannahreum.com'],
    ['Costco','Costco Wholesale','costco','us_mart','https://costco.com'],
    ['Walmart','Walmart','walmart','us_mart','https://walmart.com'],
    ['Kroger','Kroger','kroger','us_mart','https://kroger.com'],
    ['Target','Target','target','us_mart','https://target.com'],
    ['Publix','Publix','publix','us_mart','https://publix.com'],
    ['H-E-B','H-E-B','heb','us_mart','https://heb.com'],
    ['99 Ranch Market','99 Ranch Market','99ranch','asian_mart','https://99ranch.com'],
    ['Seafood City','Seafood City','seafoodcity','asian_mart','https://seafoodcity.com'],
    ['Mitsuwa','Mitsuwa Marketplace','mitsuwa','asian_mart','https://mitsuwa.com'],
    ['Weee!','Weee!','weee','online','https://sayweee.com'],
    ['울타리몰','Wooltari Mall','wooltari','online','https://wooltariusa.com'],
    ["Kim'C Market","Kim'C Market",'kimc','online','https://kimcmarket.com'],
];

$ins = $pdo->prepare("INSERT INTO shopping_stores (name,name_en,chain_name,category,website,scrape_method,is_active,created_at,updated_at) VALUES (?,?,?,?,?,'manual',1,NOW(),NOW())");
$added = 0;
foreach($newStores as $s){
    $chk = $pdo->prepare("SELECT id FROM shopping_stores WHERE chain_name=?");
    $chk->execute([$s[2]]);
    if(!$chk->fetch()){
        $ins->execute([$s[0],$s[1],$s[2],$s[3],$s[4]]);
        $added++;
        echo "  + {$s[0]}\n";
    }
}
echo "마트 추가: {$added}개\n";

// H Mart 지점
$hmartId = $pdo->query("SELECT id FROM shopping_stores WHERE chain_name='hmart' LIMIT 1")->fetchColumn();
$locs = [
    ['Duluth GA','3271 Steve Reynolds Blvd','Duluth','GA','30096',34.0007,-84.1499,'09:00','21:00'],
    ['Norcross GA','5490 Buford Hwy NE','Norcross','GA','30071',33.9412,-84.2135,'09:00','21:00'],
    ['Flushing NY','136-16 39th Ave','Flushing','NY','11354',40.7588,-73.8303,'08:00','23:00'],
    ['Fort Lee NJ','2200 Fletcher Ave','Fort Lee','NJ','07024',40.8509,-73.9701,'09:00','21:00'],
    ['Rockville MD','800 N Frederick Ave','Rockville','MD','20850',39.0840,-77.1528,'09:00','21:00'],
    ['Fairfax VA','9830 Lee Hwy','Fairfax','VA','22030',38.8462,-77.3064,'09:00','21:00'],
    ['Burlington MA','3 Wall St','Burlington','MA','01803',42.5048,-71.2120,'09:00','21:00'],
    ['Chicago IL','711 W Jackson Blvd','Chicago','IL','60661',41.8779,-87.6418,'09:00','21:00'],
    ['Houston TX','1005 Blalock Rd','Houston','TX','77055',29.7688,-95.4965,'09:00','21:00'],
    ['Carrollton TX','2625 Old Denton Rd','Carrollton','TX','75007',32.9537,-96.8903,'09:00','21:00'],
    ['Lynnwood WA','3410 196th St SW','Lynnwood','WA','98036',47.8209,-122.3151,'09:00','21:00'],
    ['Los Angeles CA','3315 W Olympic Blvd','Los Angeles','CA','90019',34.0522,-118.3427,'09:00','22:00'],
    ['Garden Grove CA','9780 Garden Grove Blvd','Garden Grove','CA','92844',33.7736,-117.9370,'09:00','21:00'],
    ['San Jose CA','245 E Hamilton Ave','Campbell','CA','95008',37.2871,-121.9500,'09:00','21:00'],
    ['Denver CO','2025 E Colfax Ave','Denver','CO','80206',39.7392,-104.9590,'09:00','21:00'],
];
$days = json_encode(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']);
$locIns = $pdo->prepare("INSERT INTO store_locations (store_id,branch_name,address,city,state,zip_code,lat,lng,open_time,close_time,open_days,is_active,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,1,NOW(),NOW())");
$la = 0;
foreach($locs as $l){
    $chk = $pdo->prepare("SELECT id FROM store_locations WHERE store_id=? AND branch_name=?");
    $chk->execute([$hmartId,$l[0]]);
    if(!$chk->fetch()){ $locIns->execute([$hmartId,$l[0],$l[1],$l[2],$l[3],$l[4],$l[5],$l[6],$l[7],$l[8],$days]); $la++; }
}
echo "H Mart 지점: {$la}개\n";

echo "\n=== 최종 통계 ===\n";
$cats = $pdo->query("SELECT category,COUNT(*) cnt FROM shopping_stores WHERE deleted_at IS NULL GROUP BY category")->fetchAll(PDO::FETCH_ASSOC);
foreach($cats as $c) echo "{$c['category']}: {$c['cnt']}개\n";
echo "총 마트: " . $pdo->query("SELECT COUNT(*) FROM shopping_stores WHERE deleted_at IS NULL")->fetchColumn() . "개\n";
echo "총 지점: " . $pdo->query("SELECT COUNT(*) FROM store_locations")->fetchColumn() . "개\n";
echo "유효 딜: " . $pdo->query("SELECT COUNT(*) FROM shopping_deals WHERE original_price>0 AND discount_percent>0")->fetchColumn() . "개\n";
@unlink(__FILE__);
