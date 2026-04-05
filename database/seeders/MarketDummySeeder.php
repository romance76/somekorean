<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class MarketDummySeeder extends Seeder
{
    public function run(): void
    {
        $userIds = DB::table('users')->pluck('id')->toArray();
        if (empty($userIds)) {
            $this->command->error('users 테이블에 데이터가 없습니다. FakeUsersSeeder를 먼저 실행하세요.');
            return;
        }

        $this->command->info('중고장터 300개 생성 중...');

        // ── 카테고리별 물품 데이터 ──
        $itemsByCategory = [
            'electronics' => [
                ['title' => '삼성 TV 65인치 급매', 'desc' => 'Samsung 65인치 4K UHD 스마트 TV. 2024년 모델. 박스/리모컨 있음. 이사로 급매합니다.', 'price' => [300, 800], 'cond' => ['like_new', 'good']],
                ['title' => '아이폰 15 Pro 256G 미개봉', 'desc' => 'iPhone 15 Pro 256GB 블랙 티타늄. 미개봉 새제품. 개통 이력 없음.', 'price' => [800, 1200], 'cond' => ['new']],
                ['title' => 'MacBook Air M2 13인치', 'desc' => '맥북에어 M2 칩. 8GB/256GB. 충전 횟수 50회 미만. 케이스 포함.', 'price' => [700, 1000], 'cond' => ['like_new', 'good']],
                ['title' => 'iPad Pro 11인치 + Apple Pencil', 'desc' => 'iPad Pro 11인치 256GB. Apple Pencil 2세대 포함. 화면 깔끔.', 'price' => [500, 800], 'cond' => ['like_new', 'good']],
                ['title' => 'Sony A7III 미러리스 카메라', 'desc' => 'Sony A7III 바디 + 28-70mm 렌즈. 셔터 카운트 1만 미만.', 'price' => [1000, 1800], 'cond' => ['good']],
                ['title' => 'AirPods Pro 2세대', 'desc' => '에어팟 프로 2세대 USB-C. 거의 안 써서 새것 같아요.', 'price' => [120, 200], 'cond' => ['like_new']],
                ['title' => 'Nintendo Switch OLED', 'desc' => '닌텐도 스위치 OLED 모델. 게임 3개 포함. 상태 양호.', 'price' => [200, 300], 'cond' => ['good']],
                ['title' => 'PS5 디스크 에디션', 'desc' => 'PS5 디스크 에디션. 컨트롤러 2개. 게임 5개 포함.', 'price' => [300, 450], 'cond' => ['good']],
                ['title' => 'Galaxy Watch 6 Classic', 'desc' => '삼성 갤럭시 워치 6 클래식 47mm. 밴드 2개 포함.', 'price' => [150, 280], 'cond' => ['like_new', 'good']],
                ['title' => 'Bose QuietComfort 헤드폰', 'desc' => 'Bose QC45 노이즈캔슬링 헤드폰. 케이스 포함. 배터리 상태 좋��.', 'price' => [150, 250], 'cond' => ['good']],
            ],
            'furniture' => [
                ['title' => '이케아 소파 반값에', 'desc' => 'IKEA KIVIK 3인용 소파 그레이. 2년 사용. 커버 세탁 가능. 이사로 급매.', 'price' => [200, 500], 'cond' => ['good', 'fair']],
                ['title' => '퀸 사이즈 매트리스 + 프레임', 'desc' => '퀸 사이즈 메모리폼 매트리스 + 나무 프레임. 1년 사용. 깨끗합니다.', 'price' => [200, 400], 'cond' => ['good']],
                ['title' => '식탁 세트 (테이블+의자4)', 'desc' => '우드 식탁 + 의자 4개 세트. 상태 양호. 직접 픽업.', 'price' => [150, 350], 'cond' => ['good', 'fair']],
                ['title' => '책상 + 사무용 의자', 'desc' => '높이 조절 가능한 컴퓨터 책상과 인체공학 의자 세트. 재택근무에 최적.', 'price' => [100, 300], 'cond' => ['good']],
                ['title' => '드레서 거울 화장대', 'desc' => '화이트 화장대 거울 포함. IKEA 제품. 깨끗하게 사용했습니다.', 'price' => [50, 150], 'cond' => ['good']],
                ['title' => 'TV 스탠드/선반', 'desc' => '65인치까지 지원하는 TV 스탠드. 수납 공간 넉넉.', 'price' => [30, 100], 'cond' => ['good', 'fair']],
                ['title' => '이케아 빌리 책장', 'desc' => 'IKEA BILLY 책장 화이트. 높이 202cm. 조립 완료 상태.', 'price' => [30, 80], 'cond' => ['good']],
            ],
            'clothing' => [
                ['title' => '나이키 에어맥스 270 새것', 'desc' => 'Nike Air Max 270 블랙/화이트. 사이즈 9. 미착용 새것.', 'price' => [80, 150], 'cond' => ['new', 'like_new']],
                ['title' => '캐나다구스 패딩 M사이즈', 'desc' => 'Canada Goose Expedition 파카 M. 2시즌 착용. 세탁 완료.', 'price' => [400, 700], 'cond' => ['good']],
                ['title' => '명품 가방 루이비통', 'desc' => 'Louis Vuitton Neverfull MM 모노그램. 정품. 더스트백 포함.', 'price' => [800, 1500], 'cond' => ['good']],
                ['title' => '한복 세트 (여성용)', 'desc' => '설날/추석용 한복 세트. 한 번 착용. S사이즈. 깨끗합니다.', 'price' => [50, 200], 'cond' => ['like_new']],
                ['title' => '골프웨어 세트', 'desc' => '남성용 골프 폴로셔츠 3벌 + 바지 2벌. L사이즈. 브랜드 혼합.', 'price' => [50, 120], 'cond' => ['good']],
            ],
            'car' => [
                ['title' => '2020 Toyota Camry LE', 'desc' => '2020 Camry LE. 마일리지 35K. 사고이력 없음. 타이어 새것.', 'price' => [18000, 23000], 'cond' => ['good']],
                ['title' => '2019 Hyundai Sonata', 'desc' => '2019 소나타 SEL. 마일리지 42K. 원오너. 정비 이력 있음.', 'price' => [15000, 19000], 'cond' => ['good']],
                ['title' => '2021 Honda Civic', 'desc' => '2021 Civic Sport. 마일리지 28K. 블랙. 옵션 풀.', 'price' => [20000, 25000], 'cond' => ['good']],
                ['title' => '2018 Kia Stinger GT', 'desc' => '기아 스팅어 GT. V6 트윈터보. 마일리지 55K. 레드.', 'price' => [22000, 28000], 'cond' => ['good', 'fair']],
            ],
            'baby' => [
                ['title' => '유아용 카시트 (Graco 4Ever)', 'desc' => 'Graco 4Ever DLX 카시트. 사고이력 없음. 세탁 완료. 2022년 구매.', 'price' => [80, 180], 'cond' => ['good']],
                ['title' => '유모차 UPPAbaby Vista V2', 'desc' => 'UPPAbaby Vista V2 유모차. 바시넷 + 시트 포함. 그레이.', 'price' => [300, 600], 'cond' => ['good']],
                ['title' => '아기 옷 묶음 (0-12개월)', 'desc' => '아기 옷 50벌 이상 묶음. 0-12개월. Carter\'s, GAP 등 브랜드.', 'price' => [30, 80], 'cond' => ['good']],
                ['title' => '유아용 장난감 세트', 'desc' => '레고 듀플로, 피셔프라이스 등 유아 장난감 모음. 상태 양호.', 'price' => [20, 60], 'cond' => ['good', 'fair']],
                ['title' => '유아용 침대 (크립)', 'desc' => 'IKEA SNIGLAR 크립 + 매트리스. 2년 사용. 깨끗합니다.', 'price' => [50, 120], 'cond' => ['good']],
            ],
            'kitchen' => [
                ['title' => '쿠쿠 밥솥 10인용', 'desc' => '쿠쿠 IH 전기압력밥솥 10인용. 1년 사용. 내솥 깨끗. 한국 직구 제품.', 'price' => [100, 250], 'cond' => ['good']],
                ['title' => '에어프라이어 Ninja 대용량', 'desc' => 'Ninja Air Fryer XL 5.5QT. 가족용. 6개월 사용.', 'price' => [40, 80], 'cond' => ['good', 'like_new']],
                ['title' => '김치 냉장고 (딤채)', 'desc' => '딤채 스탠드형 김치냉장고. 한국에서 가져온 것. 전압 변환기 포함.', 'price' => [300, 600], 'cond' => ['good']],
                ['title' => '스탠드 믹서 KitchenAid', 'desc' => 'KitchenAid Artisan 5QT 스탠드 믹서 레드. 거의 안 씀.', 'price' => [150, 280], 'cond' => ['like_new']],
                ['title' => '한국 냄비/팬 세트', 'desc' => '해피콜 프라이팬 + 냄비 세트 5개. IH 호환. 1년 사용.', 'price' => [30, 80], 'cond' => ['good']],
            ],
            'sports' => [
                ['title' => 'Peloton 바이크 풀세트', 'desc' => 'Peloton 실내 자전거 + 슈즈 + 매트. 2년 사용. 정상 작동.', 'price' => [500, 1000], 'cond' => ['good']],
                ['title' => '골프 클럽 풀세트', 'desc' => 'Callaway 골프 클럽 풀세트. 드라이버 + 아이언 + 퍼터 + 백.', 'price' => [300, 800], 'cond' => ['good']],
                ['title' => '요가 매트 + 소품 세트', 'desc' => 'Manduka 프로 요가 매트 + 블록 + 스트랩. 깨끗합니다.', 'price' => [30, 80], 'cond' => ['good', 'like_new']],
                ['title' => '덤벨 세트 5-50lb', 'desc' => '조절식 덤벨 세트 5-50lb. Bowflex SelectTech. 거의 새것.', 'price' => [200, 400], 'cond' => ['like_new', 'good']],
                ['title' => '테니스 라켓 Wilson Pro', 'desc' => 'Wilson Pro Staff 테니스 라켓. 가방 포함. 거트 새로 교체.', 'price' => [50, 150], 'cond' => ['good']],
            ],
            'instrument' => [
                ['title' => '야마하 디지털 피아노', 'desc' => 'Yamaha P-125 디지털 피아노 88건반. 스탠드 + 페달 포함. 3년 사용.', 'price' => [300, 500], 'cond' => ['good']],
                ['title' => '통기타 Taylor 214ce', 'desc' => 'Taylor 214ce 어쿠스틱 기타. 하드케이스 포함. 상태 최상.', 'price' => [500, 900], 'cond' => ['good', 'like_new']],
                ['title' => '일렉 기타 + 앰프', 'desc' => 'Fender Squier Strat + Fender Frontman 10G 앰프. 초보용 세트.', 'price' => [100, 250], 'cond' => ['good']],
                ['title' => '바이올린 풀사이즈', 'desc' => '4/4 풀사이즈 바이올린. 케이스 + 활 포함. 학생용.', 'price' => [80, 200], 'cond' => ['good']],
                ['title' => '우쿨렐레 콘서트 사이즈', 'desc' => 'Kala KA-C 콘서트 우쿨렐레. 케이스 포함. 거의 새것.', 'price' => [30, 80], 'cond' => ['like_new']],
            ],
            'etc' => [
                ['title' => '이사 정리 - 생활용품 모음', 'desc' => '이사 정리합니다. 식기류, 수건, 커튼 등 생활용품 묶음. 가져가실 분.', 'price' => [10, 50], 'cond' => ['fair', 'good']],
                ['title' => '한국 책 모음 20권', 'desc' => '소설, 에세이, 자기계발서 등 한국어 책 20권 묶음. 상태 양호.', 'price' => [20, 40], 'cond' => ['good']],
                ['title' => '캠핑 장비 세트', 'desc' => '4인용 텐트 + 침낭 2개 + 랜턴 + 쿨러. 패밀리 캠핑용.', 'price' => [100, 300], 'cond' => ['good']],
                ['title' => '여행용 캐리어 28인치', 'desc' => 'Samsonite 28인치 하드케이스 캐리어. TSA 잠금. 바퀴 정상.', 'price' => [50, 120], 'cond' => ['good']],
                ['title' => '크리스마스 트리 + 장식', 'desc' => '7피트 크리스마스 트리 + 장식 소품 세트. 박스 보관.', 'price' => [20, 60], 'cond' => ['good']],
                ['title' => '화분/관엽식물 모음', 'desc' => '몬스테라, 고무나무, 스투키 등 관엽식물 5개. 화분 포함.', 'price' => [20, 80], 'cond' => ['good']],
            ],
        ];

        $categoryKeys = array_keys($itemsByCategory);
        $regions = ['Los Angeles', 'New York', 'Atlanta', 'Chicago', 'Seattle', 'Dallas', 'Houston', 'San Francisco', 'Boston', 'Miami', 'San Jose', 'Virginia', 'New Jersey', 'Denver', 'Portland'];

        $now = Carbon::now();
        $rows = [];

        for ($i = 0; $i < 300; $i++) {
            $catKey = $categoryKeys[$i % count($categoryKeys)];
            $items = $itemsByCategory[$catKey];
            $item = $items[$i % count($items)];

            $price = rand($item['price'][0], $item['price'][1]);
            $conditions = $item['cond'];
            $condition = $conditions[array_rand($conditions)];

            // 상태: 판매중(70%), 예약중(15%), 판매완료(15%)
            $statusRand = rand(1, 100);
            if ($statusRand <= 70) {
                $status = 'active';
            } elseif ($statusRand <= 85) {
                $status = 'active'; // 예약중은 status가 active + reservation
            } else {
                $status = 'sold';
            }

            // reservation_points: 30%
            $reservationPoints = 0;
            $reservationHours = 24;
            if (rand(1, 100) <= 30) {
                $reservationPoints = rand(1, 4) * 50; // 50, 100, 150, 200
                $reservationHours = rand(0, 1) ? 24 : 48;
            }

            $daysAgo = rand(0, 90);
            $hour = rand(7, 23);
            $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute(rand(0, 59))->setSecond(rand(0, 59));

            $rows[] = [
                'user_id'            => $userIds[array_rand($userIds)],
                'title'              => $item['title'],
                'description'        => $item['desc'],
                'price'              => $price,
                'price_negotiable'   => rand(0, 100) < 40, // 40% 가격 협상 가능
                'images'             => null,
                'category'           => $catKey,
                'item_type'          => $catKey === 'car' ? 'car' : 'used',
                'region'             => $regions[array_rand($regions)],
                'condition'          => $condition,
                'view_count'         => rand(20, 1500),
                'status'             => $status,
                'reservation_points' => $reservationPoints,
                'reservation_hours'  => $reservationHours,
                'created_at'         => $createdAt,
                'updated_at'         => $createdAt,
            ];
        }

        // 50개씩 chunk insert
        foreach (array_chunk($rows, 50) as $chunk) {
            DB::table('market_items')->insert($chunk);
        }

        $this->command->info('중고장터 300개 생성 완료!');
    }
}
