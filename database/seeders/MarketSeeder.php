<?php

namespace Database\Seeders;

use App\Models\MarketItem;
use App\Models\User;
use Illuminate\Database\Seeder;

class MarketSeeder extends Seeder
{
    public function run(): void
    {
        $userIds = User::pluck('id')->toArray();
        if (empty($userIds)) { $this->command->warn('MarketSeeder: no users, skipping.'); return; }

        $categoryItems = [
            '전자기기' => [
                'titles' => ['아이폰 15 Pro 256GB 팝니다', '삼성 갤럭시 S24 팝니다', '맥북 프로 M3 14인치', '아이패드 에어 5세대', 'PS5 디스크 에디션 팝니다', '에어팟 프로 2세대 미개봉', 'LG OLED 65인치 TV', '다이슨 V15 무선 청소기', '닌텐도 스위치 OLED', '소니 WH-1000XM5 헤드폰'],
                'prices' => [400, 3000],
                'descs'  => ['구매한 지 {months}개월 됐고 상태 아주 좋습니다. 기스 없고 깨끗합니다.', '거의 새 제품입니다. 박스, 충전기 다 있습니다. 직거래 선호합니다.'],
            ],
            '가구' => [
                'titles' => ['이케아 소파 (3인용) 팝니다', '원목 식탁 + 의자 4개 세트', '킹 사이즈 매트리스', '책상 + 의자 세트', 'TV 스탠드 팝니다', '이케아 옷장 (PAX)', '가죽 소파 2인용', 'L자 컴퓨터 책상', '식기 세척기 (보쉬)', '아기 침대 + 매트리스'],
                'prices' => [50, 2000],
                'descs'  => ['이사 가면서 처분합니다. 상태 좋습니다.', '구매한 지 {months}개월 됐고 깨끗하게 사용했습니다. 직접 픽업 부탁드립니다.'],
            ],
            '의류' => [
                'titles' => ['캐나다구스 패딩 (M사이즈)', '나이키 에어맥스 270 새 신발', '자라 코트 (여성 S)', '노스페이스 플리스 자켓', '루이비통 가방 정품', '아디다스 트레이닝복 세트', '유니클로 경량 다운', '뉴발란스 993 (270)', '랄프로렌 셔츠 (L)', '코치 지갑 정품'],
                'prices' => [20, 800],
                'descs'  => ['{times}번 입었고 상태 아주 좋습니다. 사이즈 안 맞아서 팝니다.', '선물 받았는데 스타일이 안 맞아서 팝니다. 새 제품이에요.'],
            ],
            '자동차' => [
                'titles' => ['2020 현대 소나타 팝니다', '2019 토요타 캠리 LE', '2021 기아 텔루라이드', '2018 혼다 어코드', '2022 테슬라 모델3', '2020 BMW X3', '2017 렉서스 RX350', '2019 현대 투싼', '2021 기아 K5', '2020 벤츠 C300'],
                'prices' => [8000, 45000],
                'descs'  => ['마일리지 {miles}마일, 사고 이력 없습니다. 오일 체인지 정기적으로 했습니다.', '깨끗하게 관리했습니다. 타이틀 클린이고 카팩스 제공 가능합니다.'],
            ],
            '유아용품' => [
                'titles' => ['유모차 (업파베이비 비스타) 팝니다', '카시트 (그라코) 팝니다', '아기 옷 뭉탱이 (0~12개월)', '범보 의자 + 트레이', '아기 바운서 팝니다', '젖병 소독기 새 제품', '수유 쿠션 팝니다', '아기 보행기 팝니다', '아기 욕조 + 목욕용품 세트', '유아용 그네 (실내용)'],
                'prices' => [10, 500],
                'descs'  => ['아기가 커서 정리합니다. 상태 좋습니다.', '거의 안 썼어요. 새 것과 다름없습니다.'],
            ],
            '스포츠' => [
                'titles' => ['골프 클럽 세트 (테일러메이드)', '자전거 (스페셜라이즈드)', '테니스 라켓 (윌슨)', '캠핑 텐트 4인용', '요가 매트 + 블록 세트', '덤벨 세트 (5~30파운드)', '스키 장비 세트', '서핑보드 팝니다', '러닝머신 (NordicTrack)', '농구공 + 축구공 세트'],
                'prices' => [15, 1500],
                'descs'  => ['취미로 사용하다가 안 하게 되어 팝니다. 상태 좋습니다.', '한 시즌만 사용했습니다. 깨끗해요.'],
            ],
            '도서' => [
                'titles' => ['한국어 소설 10권 세트', 'SAT 교재 모음', '요리책 (한식/양식) 팝니다', 'TOEFL 교재 세트', '아이 영어 동화책 20권', '자기계발서 모음', '한국사 관련 도서', '프로그래밍 교재 세트', '유아 한글 교재', '대학 교과서 (경영학)'],
                'prices' => [5, 100],
                'descs'  => ['깨끗하게 보관했습니다. 낙서 없어요.', '더 이상 필요 없어서 팝니다. 상태 좋습니다.'],
            ],
            '기타' => [
                'titles' => ['이사 짐 정리 세일', '주방용품 일괄 처분', '화분 + 식물 팝니다', '크리스마스 트리 팝니다', '피아노 (디지털) 팝니다', '에어컨 (창문형) 팝니다', '공기청정기 팝니다', '전기 자전거 팝니다', '가습기 + 제습기 세트', '캐리어 (28인치) 팝니다'],
                'prices' => [10, 1000],
                'descs'  => ['이사/정리하면서 처분합니다. 상태 확인 후 가격 조율 가능합니다.', '필요 없어져서 팝니다. 직거래 선호합니다.'],
            ],
        ];

        $conditions = ['new', 'like_new', 'good', 'fair'];
        $condWeights = [10, 25, 50, 15]; // percentage
        $cities = [
            ['city' => 'Los Angeles',   'state' => 'CA', 'lat' => 34.0522,  'lng' => -118.2437],
            ['city' => 'New York',      'state' => 'NY', 'lat' => 40.7128,  'lng' => -74.0060],
            ['city' => 'Chicago',       'state' => 'IL', 'lat' => 41.8781,  'lng' => -87.6298],
            ['city' => 'Atlanta',       'state' => 'GA', 'lat' => 33.7490,  'lng' => -84.3880],
            ['city' => 'Dallas',        'state' => 'TX', 'lat' => 32.7767,  'lng' => -96.7970],
            ['city' => 'Houston',       'state' => 'TX', 'lat' => 29.7604,  'lng' => -95.3698],
            ['city' => 'Seattle',       'state' => 'WA', 'lat' => 47.6062,  'lng' => -122.3321],
            ['city' => 'San Francisco', 'state' => 'CA', 'lat' => 37.7749,  'lng' => -122.4194],
            ['city' => 'Washington',    'state' => 'DC', 'lat' => 38.9072,  'lng' => -77.0369],
            ['city' => 'Philadelphia',  'state' => 'PA', 'lat' => 39.9526,  'lng' => -75.1652],
        ];

        $now = now();
        $rows = [];
        $catKeys = array_keys($categoryItems);

        for ($i = 0; $i < 300; $i++) {
            $catKey  = $catKeys[array_rand($catKeys)];
            $catData = $categoryItems[$catKey];
            $city    = $cities[array_rand($cities)];
            $title   = $catData['titles'][array_rand($catData['titles'])];
            $priceMin = $catData['prices'][0];
            $priceMax = $catData['prices'][1];
            $price   = rand($priceMin, $priceMax);
            $desc    = str_replace(
                ['{months}', '{times}', '{miles}'],
                [rand(1, 24), rand(1, 5), number_format(rand(15000, 80000))],
                $catData['descs'][array_rand($catData['descs'])]
            );

            // Status: 80% active, 10% reserved, 10% sold
            $r = rand(1, 100);
            $status = $r <= 80 ? 'active' : ($r <= 90 ? 'reserved' : 'sold');

            // Condition weighted
            $cr = rand(1, 100);
            if ($cr <= 10) $condition = 'new';
            elseif ($cr <= 35) $condition = 'like_new';
            elseif ($cr <= 85) $condition = 'good';
            else $condition = 'fair';

            $content = "{$title}\n\n{$desc}\n\n가격: \${$price}\n상태: " . ['new' => '새 제품', 'like_new' => '거의 새 것', 'good' => '상태 좋음', 'fair' => '사용감 있음'][$condition] . "\n\n직거래 선호합니다. {$city['city']} 지역에서 만날 수 있습니다.\n가격 약간 네고 가능합니다.";

            $rows[] = [
                'user_id'       => $userIds[array_rand($userIds)],
                'title'         => $title,
                'content'       => $content,
                'price'         => $price,
                'images'        => null,
                'category'      => $catKey,
                'condition'     => $condition,
                'lat'           => round($city['lat'] + rand(-200, 200) / 10000, 7),
                'lng'           => round($city['lng'] + rand(-200, 200) / 10000, 7),
                'city'          => $city['city'],
                'state'         => $city['state'],
                'status'        => $status,
                'view_count'    => rand(5, 400),
                'is_negotiable' => rand(0, 1),
                'created_at'    => $now->copy()->subDays(rand(0, 60))->subHours(rand(0, 23)),
                'updated_at'    => $now,
            ];
        }

        foreach (array_chunk($rows, 50) as $chunk) {
            MarketItem::insert($chunk);
        }

        $this->command->info('MarketSeeder: 300 market items created');
    }
}
