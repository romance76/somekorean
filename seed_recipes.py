import paramiko, base64, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=30):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', 'replace').strip()

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+3000] for i in range(0, len(enc), 3000)]
    ssh('> /tmp/_w.b64')
    for ch in chunks:
        ssh("echo -n '{}' >> /tmp/_w.b64".format(ch))
    return ssh('base64 -d /tmp/_w.b64 > {} && rm /tmp/_w.b64 && echo OK'.format(path))

seed_php = """<?php
require __DIR__ . '/vendor/autoload.php';
$app = require __DIR__ . '/bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

use App\\Models\\RecipePost;

$userId = 272;
$recipes = [
    [
        'title' => '김치찌개',
        'intro' => '미국에서 쉽게 구할 수 있는 재료로 만드는 정통 김치찌개',
        'category_id' => 1, 'difficulty' => '쉬움', 'cook_time' => '30분', 'servings' => 4,
        'image_url' => 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
        'ingredients' => [['name'=>'묵은 김치','amount'=>'2컵'],['name'=>'돼지고기','amount'=>'200g'],['name'=>'두부','amount'=>'1/2모'],['name'=>'고추장','amount'=>'1T'],['name'=>'참기름','amount'=>'1t']],
        'steps' => [['text'=>'김치를 먹기 좋은 크기로 썰고 돼지고기도 준비합니다'],['text'=>'냄비에 참기름을 두르고 돼지고기와 김치를 볶습니다'],['text'=>'물 3컵을 붓고 끓이다가 두부를 넣습니다'],['text'=>'고추장으로 간을 맞추고 10분 더 끓입니다']],
        'tips' => ['신김치일수록 더 맛있어요', '돼지고기 대신 참치캔을 써도 됩니다'],
        'tags' => ['김치','찌개','한식','쉬운요리'],
    ],
    [
        'title' => '불고기',
        'intro' => '달콤짭짤한 양념에 재운 부드러운 소고기 불고기',
        'category_id' => 1, 'difficulty' => '보통', 'cook_time' => '45분', 'servings' => 4,
        'image_url' => 'https://images.unsplash.com/photo-1583224964978-2257b8a8d849?w=400',
        'ingredients' => [['name'=>'소고기(채끝)','amount'=>'500g'],['name'=>'간장','amount'=>'4T'],['name'=>'설탕','amount'=>'2T'],['name'=>'참기름','amount'=>'1T'],['name'=>'마늘','amount'=>'3쪽'],['name'=>'배(갈아서)','amount'=>'1/4개']],
        'steps' => [['text'=>'소고기를 얇게 썰어 준비합니다'],['text'=>'간장, 설탕, 참기름, 다진마늘, 간 배를 섞어 양념장을 만듭니다'],['text'=>'소고기에 양념장을 넣어 30분 이상 재웁니다'],['text'=>'달군 팬에 볶거나 그릴에 구워냅니다']],
        'tips' => ['배 대신 키위를 써도 고기가 부드러워져요'],
        'tags' => ['불고기','소고기','BBQ','한식'],
    ],
    [
        'title' => '된장찌개',
        'intro' => '구수하고 건강한 전통 된장찌개',
        'category_id' => 1, 'difficulty' => '쉬움', 'cook_time' => '20분', 'servings' => 2,
        'image_url' => 'https://images.unsplash.com/photo-1614777735417-6e6bc3af2c8a?w=400',
        'ingredients' => [['name'=>'된장','amount'=>'2T'],['name'=>'두부','amount'=>'1/2모'],['name'=>'호박','amount'=>'1/2개'],['name'=>'양파','amount'=>'1/4개'],['name'=>'버섯','amount'=>'한줌']],
        'steps' => [['text'=>'멸치 육수 또는 물 2컵을 끓입니다'],['text'=>'된장을 풀어 넣고 채소를 썰어 넣습니다'],['text'=>'두부를 깍둑썰기 하여 넣고 15분 끓입니다']],
        'tips' => ['된장은 좋은 재래 된장을 사용하세요','Hmart에서 쉽게 구할 수 있어요'],
        'tags' => ['된장','찌개','건강식','한식'],
    ],
    [
        'title' => '잡채',
        'intro' => '쫄깃한 당면과 알록달록 채소의 명절 요리',
        'category_id' => 1, 'difficulty' => '보통', 'cook_time' => '1시간', 'servings' => 6,
        'image_url' => 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=400',
        'ingredients' => [['name'=>'당면','amount'=>'200g'],['name'=>'시금치','amount'=>'한줌'],['name'=>'당근','amount'=>'1/2개'],['name'=>'버섯','amount'=>'3개'],['name'=>'소고기','amount'=>'100g'],['name'=>'간장','amount'=>'3T'],['name'=>'참기름','amount'=>'2T']],
        'steps' => [['text'=>'당면을 물에 30분 불립니다'],['text'=>'채소와 고기를 각각 볶아 준비합니다'],['text'=>'당면을 삶아 간장과 참기름으로 밑간합니다'],['text'=>'모든 재료를 합쳐 버무립니다']],
        'tips' => ['당면은 너무 오래 삶으면 퍼져요'],
        'tags' => ['잡채','당면','명절음식','한식'],
    ],
    [
        'title' => '갈비찜',
        'intro' => '특별한 날 만드는 부드러운 갈비찜',
        'category_id' => 1, 'difficulty' => '어려움', 'cook_time' => '1시간 이상', 'servings' => 6,
        'image_url' => 'https://images.unsplash.com/photo-1606756790138-261d2b21cd75?w=400',
        'ingredients' => [['name'=>'갈비','amount'=>'1kg'],['name'=>'간장','amount'=>'5T'],['name'=>'설탕','amount'=>'3T'],['name'=>'배','amount'=>'1/2개'],['name'=>'마늘','amount'=>'5쪽'],['name'=>'당근','amount'=>'1개'],['name'=>'감자','amount'=>'2개']],
        'steps' => [['text'=>'갈비를 찬물에 1시간 담가 핏물을 뺍니다'],['text'=>'끓는 물에 갈비를 데친 후 씻습니다'],['text'=>'양념 재료를 모두 섞어 갈비에 재웁니다'],['text'=>'냄비에 물과 함께 1시간 이상 푹 끓입니다'],['text'=>'당근, 감자를 넣고 30분 더 끓입니다']],
        'tips' => ['압력솥을 사용하면 시간이 단축됩니다'],
        'tags' => ['갈비찜','찜요리','명절음식','소고기'],
    ],
];

foreach ($recipes as $data) {
    RecipePost::create(array_merge($data, ['user_id' => $userId, 'source' => 'user']));
    echo "Inserted: " . $data['title'] . PHP_EOL;
}
echo "Total user recipes: " . RecipePost::where('source','user')->count() . PHP_EOL;
"""

print(write_file('/tmp/seed_recipes.php', seed_php))
result = ssh('cd /var/www/somekorean && php /tmp/seed_recipes.php 2>&1 && rm -f /tmp/seed_recipes.php')
print(result)
c.close()
