<?php
set_time_limit(300);
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "=== Recipe Tasks 시작 ===\n";
echo "시작 시간: " . date('Y-m-d H:i:s') . "\n\n";

// ──────────────────────────────────────────────
// DB 연결 (debian-sys-maint 사용)
// ──────────────────────────────────────────────
$dbHost = '127.0.0.1';
$dbPort = '3306';
$dbName = 'somekorean';
$dbUser = 'debian-sys-maint';
$dbPass = 'CX9xCHzYCsiFfbI2';
// socket 연결
$dsn = "mysql:unix_socket=/var/run/mysqld/mysqld.sock;dbname={$dbName};charset=utf8mb4";

try {
    $pdo = new PDO($dsn, $dbUser, $dbPass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
    echo "DB 연결 성공\n\n";
} catch (Exception $e) {
    // fallback: TCP 연결
    try {
        $dsn2 = "mysql:host={$dbHost};port={$dbPort};dbname={$dbName};charset=utf8mb4";
        $pdo = new PDO($dsn2, 'somekorean_user', 'SK_DB@2026!secure', [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);
        echo "DB 연결 성공 (fallback TCP)\n\n";
    } catch (Exception $e2) {
        die("DB 연결 실패: " . $e2->getMessage() . "\n");
    }
}

// ──────────────────────────────────────────────
// 관리자 user_id 확인
// ──────────────────────────────────────────────
$adminUserId = 1;
try {
    $stmt = $pdo->query("SELECT id FROM users WHERE is_admin = 1 ORDER BY id LIMIT 1");
    $row = $stmt->fetch();
    if ($row) {
        $adminUserId = (int)$row['id'];
    }
} catch (Exception $e) {}
echo "관리자 user_id: {$adminUserId}\n\n";

// 전체 user_id 목록 (좋아요/댓글용)
$allUserIds = [];
try {
    $stmt = $pdo->query("SELECT id FROM users ORDER BY id LIMIT 200");
    while ($row = $stmt->fetch()) {
        $allUserIds[] = (int)$row['id'];
    }
} catch (Exception $e) {}
echo "전체 유저 수: " . count($allUserIds) . "\n\n";

// category_id 기본값 (korean 카테고리)
$defaultCategoryId = 1;
try {
    $stmt = $pdo->query("SELECT id FROM recipe_categories LIMIT 1");
    $row = $stmt->fetch();
    if ($row) $defaultCategoryId = (int)$row['id'];
} catch (Exception $e) {}

// ══════════════════════════════════════════════
// 작업 1: 불완전한 레시피 삭제
// ══════════════════════════════════════════════
echo "=== 작업 1 시작: 불완전한 레시피 삭제 ===\n";

try {
    // 삭제 전 카운트
    $total = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_posts")->fetch()['cnt'];
    echo "삭제 전 총 레시피 수: {$total}\n";

    // 불완전한 레시피 수 확인
    $countSql = "SELECT COUNT(*) as cnt FROM recipe_posts WHERE
        (image_url IS NULL OR image_url = '')
        OR (title IS NULL OR title = '')
        OR (ingredients IS NULL OR ingredients = '' OR ingredients = '[]' OR ingredients = 'null')
        OR (steps IS NULL OR steps = '' OR steps = '[]' OR steps = 'null')";
    $incomplete = $pdo->query($countSql)->fetch()['cnt'];
    echo "불완전한 레시피 수: {$incomplete}\n";

    if ($incomplete > 0) {
        $delSql = "DELETE FROM recipe_posts WHERE
            (image_url IS NULL OR image_url = '')
            OR (title IS NULL OR title = '')
            OR (ingredients IS NULL OR ingredients = '' OR ingredients = '[]' OR ingredients = 'null')
            OR (steps IS NULL OR steps = '' OR steps = '[]' OR steps = 'null')";
        $deleted = $pdo->exec($delSql);
        echo "삭제된 레시피 수: {$deleted}\n";
    }

    $remaining = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_posts")->fetch()['cnt'];
    echo "삭제 후 남은 레시피 수: {$remaining}\n";
} catch (Exception $e) {
    echo "작업 1 오류: " . $e->getMessage() . "\n";
}
echo "\n";

// ══════════════════════════════════════════════
// 작업 2: TheMealDB API로 레시피 추가
// ══════════════════════════════════════════════
echo "=== 작업 2 시작: TheMealDB API로 레시피 추가 ===\n";

function fetchUrl($url) {
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0');
        $result = curl_exec($ch);
        $err = curl_error($ch);
        curl_close($ch);
        if ($err) return false;
        return $result;
    }
    $ctx = stream_context_create(['http' => ['timeout' => 30, 'user_agent' => 'Mozilla/5.0']]);
    return @file_get_contents($url, false, $ctx);
}

try {
    // 기존 title 목록
    $existingTitles = [];
    $stmt = $pdo->query("SELECT title FROM recipe_posts");
    while ($row = $stmt->fetch()) {
        $existingTitles[strtolower(trim($row['title']))] = true;
    }

    $insertCount = 0;
    $skipCount = 0;

    // 검색어 목록 (TheMealDB에 한국 음식 데이터가 없으므로 다양한 글로벌 레시피 추가)
    $searchTerms = ['beef', 'chicken', 'pork', 'soup', 'lamb', 'salad', 'fish', 'rice', 'noodle', 'potato'];

    foreach ($searchTerms as $term) {
        echo "검색 중: {$term}\n";
        $searchUrl = "https://www.themealdb.com/api/json/v1/1/search.php?s=" . urlencode($term);
        $data = fetchUrl($searchUrl);
        if (!$data) {
            echo "  API 호출 실패: {$searchUrl}\n";
            continue;
        }
        $json = json_decode($data, true);
        if (!$json || !isset($json['meals']) || !$json['meals']) {
            echo "  결과 없음\n";
            continue;
        }

        foreach ($json['meals'] as $meal) {
            $title = trim($meal['strMeal'] ?? '');
            if (!$title) { $skipCount++; continue; }

            // 중복 체크
            if (isset($existingTitles[strtolower($title)])) {
                echo "  스킵(중복): {$title}\n";
                $skipCount++;
                continue;
            }

            $imageUrl = trim($meal['strMealThumb'] ?? '');
            if (!$imageUrl) {
                echo "  스킵(이미지 없음): {$title}\n";
                $skipCount++;
                continue;
            }

            // ingredients 조합
            $ingredients = [];
            for ($i = 1; $i <= 20; $i++) {
                $name = trim($meal["strIngredient{$i}"] ?? '');
                $amount = trim($meal["strMeasure{$i}"] ?? '');
                if ($name) {
                    $ingredients[] = ['name' => $name, 'amount' => $amount];
                }
            }
            if (empty($ingredients)) {
                echo "  스킵(재료 없음): {$title}\n";
                $skipCount++;
                continue;
            }

            // steps 조합
            $instructions = trim($meal['strInstructions'] ?? '');
            $steps = [];
            if ($instructions) {
                $lines = preg_split('/\r?\n+/', $instructions);
                $stepNum = 1;
                foreach ($lines as $line) {
                    $line = trim($line);
                    if ($line && strlen($line) > 3) {
                        // STEP 숫자 등 제거
                        $line = preg_replace('/^(STEP\s*\d+[\.\:\-]?\s*)/i', '', $line);
                        if (trim($line)) {
                            $steps[] = ['step' => $stepNum++, 'description' => $line];
                        }
                    }
                }
            }
            if (empty($steps)) {
                echo "  스킵(단계 없음): {$title}\n";
                $skipCount++;
                continue;
            }

            // tip
            $tip = null;
            if (!empty($meal['strSource'])) {
                $tip = "출처: " . $meal['strSource'];
            }

            // created_at 랜덤 (1년 이내)
            $daysAgo = rand(30, 365);
            $createdAt = date('Y-m-d H:i:s', strtotime("-{$daysAgo} days"));

            try {
                $insertSql = "INSERT INTO recipe_posts
                    (category_id, user_id, title, difficulty, cook_time, servings, ingredients, steps, image_url, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
                $stmt = $pdo->prepare($insertSql);
                $stmt->execute([
                    $defaultCategoryId,
                    $adminUserId,
                    $title,
                    'medium',
                    '30분',
                    4,
                    json_encode($ingredients, JSON_UNESCAPED_UNICODE),
                    json_encode($steps, JSON_UNESCAPED_UNICODE),
                    $imageUrl,
                    'themealdb',
                    $createdAt,
                    $createdAt,
                ]);
                $existingTitles[strtolower($title)] = true;
                $insertCount++;
                echo "  추가: {$title}\n";
            } catch (Exception $e) {
                echo "  INSERT 오류({$title}): " . $e->getMessage() . "\n";
                $skipCount++;
            }
        }
        // API 부하 방지
        sleep(1);
    }

    echo "\n추가된 레시피: {$insertCount}개, 스킵: {$skipCount}개\n";
    $newTotal = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_posts")->fetch()['cnt'];
    echo "현재 총 레시피 수: {$newTotal}\n";
} catch (Exception $e) {
    echo "작업 2 오류: " . $e->getMessage() . "\n";
}
echo "\n";

// ══════════════════════════════════════════════
// 작업 3: recipe_likes 테이블 생성 및 랜덤 좋아요
// ══════════════════════════════════════════════
echo "=== 작업 3 시작: recipe_likes 테이블 및 랜덤 좋아요 ===\n";

try {
    $pdo->exec("CREATE TABLE IF NOT EXISTS recipe_likes (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        recipe_id BIGINT UNSIGNED NOT NULL,
        user_id BIGINT UNSIGNED NOT NULL,
        created_at TIMESTAMP NULL,
        UNIQUE KEY unique_like (recipe_id, user_id)
    )");
    echo "recipe_likes 테이블 준비 완료\n";

    // 기존 좋아요 수 확인
    $existingLikes = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_likes")->fetch()['cnt'];
    echo "기존 좋아요 수: {$existingLikes}\n";

    // 모든 레시피 가져오기
    $recipes = $pdo->query("SELECT id, created_at FROM recipe_posts ORDER BY id")->fetchAll();
    echo "대상 레시피 수: " . count($recipes) . "\n";

    if (empty($allUserIds)) {
        echo "유저 없음 - 스킵\n";
    } else {
        $insertedLikes = 0;
        $today = time();

        foreach ($recipes as $recipe) {
            $recipeId = (int)$recipe['id'];
            $recipeCreatedAt = strtotime($recipe['created_at']);
            if (!$recipeCreatedAt) $recipeCreatedAt = strtotime('-1 year');

            $likeCount = rand(5, 47);
            // 랜덤 유저 선택
            $shuffled = $allUserIds;
            shuffle($shuffled);
            $selectedUsers = array_slice($shuffled, 0, min($likeCount, count($shuffled)));

            foreach ($selectedUsers as $userId) {
                $likeTime = rand($recipeCreatedAt, $today);
                $likeAt = date('Y-m-d H:i:s', $likeTime);
                try {
                    $pdo->prepare("INSERT IGNORE INTO recipe_likes (recipe_id, user_id, created_at) VALUES (?, ?, ?)")
                        ->execute([$recipeId, $userId, $likeAt]);
                    $insertedLikes++;
                } catch (Exception $e) {
                    // 중복 무시
                }
            }
        }
        echo "추가된 좋아요: {$insertedLikes}개\n";

        // like_count 업데이트
        $pdo->exec("UPDATE recipe_posts rp SET like_count = (SELECT COUNT(*) FROM recipe_likes rl WHERE rl.recipe_id = rp.id)");
        echo "like_count 업데이트 완료\n";
    }

    $totalLikes = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_likes")->fetch()['cnt'];
    echo "총 좋아요 수: {$totalLikes}\n";
} catch (Exception $e) {
    echo "작업 3 오류: " . $e->getMessage() . "\n";
}
echo "\n";

// ══════════════════════════════════════════════
// 작업 4: recipe_comments 댓글 추가
// ══════════════════════════════════════════════
echo "=== 작업 4 시작: recipe_comments 랜덤 댓글 ===\n";

$commentTexts = [
    "진짜 맛있었어요! 가족들이 너무 좋아했어요 👍",
    "생각보다 어렵지 않네요. 초보도 할 수 있어요!",
    "재료 손질이 좀 걸리지만 결과물은 최고예요",
    "팁 대로 했더니 훨씬 맛있었어요. 감사합니다!",
    "다음엔 치즈 올려서 해볼게요 ㅎㅎ",
    "우리 아이가 엄청 잘 먹었어요. 강추!",
    "양념 비율이 딱 맞네요. 레스토랑 맛 나요",
    "냉장고에 있는 재료로 대충 했는데도 맛있어요",
    "이거 처음 해봤는데 성공했어요!! 너무 행복 ㅠㅠ",
    "간이 좀 강한 편이에요. 간장 조금 줄이는 게 나을 것 같아요",
    "사진보다 실제로 훨씬 맛있어요!",
    "만들기 쉽고 맛있어서 자주 해먹을 것 같아요",
    "재료 구하기가 좀 어렵네요. 대체 재료 알려주실 분?",
    "완전 성공! 남편이 맛있다고 또 만들어달래요 ❤️",
    "처음엔 실패했는데 두 번째엔 완벽했어요",
    "불 조절이 중요한 것 같아요. 약불로 천천히 하세요",
    "한 번에 두 배로 만들어서 냉동해뒀어요!",
    "저는 고춧가루 좀 더 넣었는데 더 맛있었어요 🌶️",
];

try {
    // recipe_comments 테이블 생성 (이미 존재하면 무시)
    $pdo->exec("CREATE TABLE IF NOT EXISTS recipe_comments (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        recipe_id BIGINT UNSIGNED NOT NULL,
        user_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL
    )");
    echo "recipe_comments 테이블 준비 완료\n";

    $existingComments = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_comments")->fetch()['cnt'];
    echo "기존 댓글 수: {$existingComments}\n";

    // 기존 댓글 없을 때만 추가 (이미 있으면 스킵)
    if ($existingComments > 0) {
        echo "기존 댓글이 있으므로 추가 스킵\n";
    } else {
        $recipes = $pdo->query("SELECT id, created_at FROM recipe_posts ORDER BY id")->fetchAll();
        $insertedComments = 0;
        $today = time();

        if (empty($allUserIds)) {
            echo "유저 없음 - 스킵\n";
        } else {
            foreach ($recipes as $recipe) {
                $recipeId = (int)$recipe['id'];
                $recipeCreatedAt = strtotime($recipe['created_at']);
                if (!$recipeCreatedAt) $recipeCreatedAt = strtotime('-1 year');

                $commentCount = rand(2, 11);
                for ($i = 0; $i < $commentCount; $i++) {
                    $userId = $allUserIds[array_rand($allUserIds)];
                    $content = $commentTexts[array_rand($commentTexts)];
                    $commentTime = rand($recipeCreatedAt, $today);
                    $commentAt = date('Y-m-d H:i:s', $commentTime);

                    try {
                        $pdo->prepare("INSERT INTO recipe_comments (recipe_id, user_id, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)")
                            ->execute([$recipeId, $userId, $content, $commentAt, $commentAt]);
                        $insertedComments++;
                    } catch (Exception $e) {
                        echo "댓글 INSERT 오류: " . $e->getMessage() . "\n";
                    }
                }
            }
            echo "추가된 댓글: {$insertedComments}개\n";
        }
    }

    $totalComments = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_comments")->fetch()['cnt'];
    echo "총 댓글 수: {$totalComments}\n";
} catch (Exception $e) {
    echo "작업 4 오류: " . $e->getMessage() . "\n";
}
echo "\n";

// ══════════════════════════════════════════════
// 작업 5: 통계 출력
// ══════════════════════════════════════════════
echo "=== 작업 5 시작: 통계 출력 ===\n";

try {
    $totalRecipes = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_posts")->fetch()['cnt'];
    echo "전체 레시피 수: {$totalRecipes}\n";

    $withImage = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_posts WHERE image_url IS NOT NULL AND image_url != ''")->fetch()['cnt'];
    echo "이미지 있는 레시피 수: {$withImage}\n";

    $totalLikes = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_likes")->fetch()['cnt'];
    echo "총 좋아요 수: {$totalLikes}\n";

    $totalComments = $pdo->query("SELECT COUNT(*) as cnt FROM recipe_comments")->fetch()['cnt'];
    echo "총 댓글 수: {$totalComments}\n";

    if ($totalRecipes > 0) {
        $avgLikes = round($totalLikes / $totalRecipes, 2);
        echo "레시피별 평균 좋아요: {$avgLikes}\n";

        $avgComments = round($totalComments / $totalRecipes, 2);
        echo "레시피별 평균 댓글: {$avgComments}\n";
    }

    // 좋아요 TOP 5
    echo "\n[좋아요 TOP 5]\n";
    $top5 = $pdo->query("
        SELECT rp.title, COUNT(rl.id) as likes
        FROM recipe_posts rp
        LEFT JOIN recipe_likes rl ON rp.id = rl.recipe_id
        GROUP BY rp.id, rp.title
        ORDER BY likes DESC
        LIMIT 5
    ")->fetchAll();
    foreach ($top5 as $row) {
        echo "  {$row['title']}: {$row['likes']}개\n";
    }

} catch (Exception $e) {
    echo "작업 5 오류: " . $e->getMessage() . "\n";
}

echo "\n=== 모든 작업 완료 ===\n";
echo "종료 시간: " . date('Y-m-d H:i:s') . "\n";
