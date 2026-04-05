<?php

namespace Database\Seeders;

use App\Models\RealEstateListing;
use App\Models\User;
use Illuminate\Database\Seeder;

class RealEstateSeeder extends Seeder
{
    public function run(): void
    {
        $userIds = User::pluck('id')->toArray();
        if (empty($userIds)) { $this->command->warn('RealEstateSeeder: no users, skipping.'); return; }

        $rentTitles = [
            '깨끗한 원베드 아파트 렌트', '방 2개 아파트 즉시 입주 가능', '스튜디오 아파트 렌트',
            '한인타운 2BR/1BA 아파트', '조용한 동네 원룸 렌트', '신축 아파트 렌트',
            '리모델링 완료 2베드 아파트', '유틸리티 포함 원베드', '학교 근처 패밀리 아파트',
            '게이트 단지 내 아파트 렌트', '주차 포함 아파트 렌트', '워셔/드라이어 인유닛 아파트',
        ];

        $saleTitles = [
            '3BR/2BA 단독주택 매매', '콘도 2BR 매매합니다', '타운하우스 3BR 매매',
            '럭셔리 콘도 매매', '신축 주택 매매', '정원 있는 단독주택 매매',
            '오피스 공간 매매', '투자용 듀플렉스 매매', '학군 좋은 지역 주택',
            '풀 있는 단독주택 매매',
        ];

        $roommateTitles = [
            '룸메이트 구합니다 (여성)', '룸메이트 구합니다 (남성)', '마스터룸 쉐어',
            '깨끗한 방 하나 서브릿', '유학생 룸메이트 구합니다', '직장인 룸메이트 구함',
            '2인 쉐어 룸메이트', '단기 룸메이트 구합니다', '반려동물 가능 룸메이트',
        ];

        $propertyTypes = ['apt', 'house', 'condo', 'studio', 'office'];
        $types = ['rent', 'sale', 'roommate'];

        $cities = [
            ['city' => 'Los Angeles',   'state' => 'CA', 'lat' => 34.0522,  'lng' => -118.2437, 'zips' => ['90004','90005','90010','90019','90020']],
            ['city' => 'New York',      'state' => 'NY', 'lat' => 40.7128,  'lng' => -74.0060,  'zips' => ['10001','10002','10016','11354','11355']],
            ['city' => 'Chicago',       'state' => 'IL', 'lat' => 41.8781,  'lng' => -87.6298,  'zips' => ['60601','60614','60625','60640','60657']],
            ['city' => 'Atlanta',       'state' => 'GA', 'lat' => 33.7490,  'lng' => -84.3880,  'zips' => ['30305','30306','30326','30338','30341']],
            ['city' => 'Dallas',        'state' => 'TX', 'lat' => 32.7767,  'lng' => -96.7970,  'zips' => ['75006','75024','75062','75075','75201']],
            ['city' => 'Houston',       'state' => 'TX', 'lat' => 29.7604,  'lng' => -95.3698,  'zips' => ['77036','77042','77056','77077','77082']],
            ['city' => 'Seattle',       'state' => 'WA', 'lat' => 47.6062,  'lng' => -122.3321, 'zips' => ['98101','98104','98109','98122','98133']],
            ['city' => 'San Francisco', 'state' => 'CA', 'lat' => 37.7749,  'lng' => -122.4194, 'zips' => ['94102','94107','94109','94112','94118']],
            ['city' => 'Washington',    'state' => 'DC', 'lat' => 38.9072,  'lng' => -77.0369,  'zips' => ['20001','20002','20005','20009','20036']],
            ['city' => 'Philadelphia',  'state' => 'PA', 'lat' => 39.9526,  'lng' => -75.1652,  'zips' => ['19102','19103','19106','19107','19130']],
        ];

        $addresses = [
            '123 Main St', '456 Oak Ave', '789 Pine Blvd', '234 Maple Dr', '567 Elm St',
            '890 Cedar Rd', '345 Birch Ln', '678 Walnut Way', '901 Cherry Ct', '432 Spruce Ave',
            '765 Willow St', '198 Palm Blvd', '543 Ash Dr', '876 Cypress Ln', '210 Magnolia Way',
        ];

        $now  = now();
        $rows = [];

        for ($i = 0; $i < 300; $i++) {
            $type = $types[array_rand($types)];
            $city = $cities[array_rand($cities)];

            // Choose title based on type
            if ($type === 'rent') {
                $title = $rentTitles[array_rand($rentTitles)];
                $propertyType = ['apt', 'studio', 'condo'][array_rand(['apt', 'studio', 'condo'])];
                $price = rand(8, 35) * 100; // $800 - $3500/mo
                $deposit = $price * rand(1, 2);
                $bedrooms = rand(0, 3);
                $bathrooms = rand(1, 2);
                $sqft = rand(400, 1800);
            } elseif ($type === 'sale') {
                $title = $saleTitles[array_rand($saleTitles)];
                $propertyType = ['house', 'condo', 'apt', 'office'][array_rand(['house', 'condo', 'apt', 'office'])];
                $price = rand(200, 1500) * 1000; // $200k - $1.5M
                $deposit = null;
                $bedrooms = rand(1, 5);
                $bathrooms = rand(1, 4);
                $sqft = rand(800, 4000);
            } else {
                $title = $roommateTitles[array_rand($roommateTitles)];
                $propertyType = ['apt', 'house', 'condo'][array_rand(['apt', 'house', 'condo'])];
                $price = rand(4, 12) * 100; // $400 - $1200/mo
                $deposit = $price;
                $bedrooms = 1;
                $bathrooms = 1;
                $sqft = rand(100, 400);
            }

            $typeKo = ['rent' => '렌트', 'sale' => '매매', 'roommate' => '룸메이트'][  $type];
            $propKo = ['apt' => '아파트', 'house' => '주택', 'condo' => '콘도', 'studio' => '스튜디오', 'office' => '오피스'][$propertyType];

            $content = "{$title}\n\n유형: {$typeKo}\n건물 타입: {$propKo}\n방: {$bedrooms}개 / 욕실: {$bathrooms}개\n면적: {$sqft} sqft\n가격: \$" . number_format($price) . ($type !== 'sale' ? '/월' : '') . "\n";
            if ($deposit) $content .= "디파짓: \$" . number_format($deposit) . "\n";
            $content .= "\n위치: {$city['city']}, {$city['state']}\n";
            $content .= "\n깨끗하고 관리 잘 된 " . $propKo . "입니다. ";
            if ($type === 'rent') {
                $content .= "즉시 입주 가능합니다. 크레딧 체크 필요합니다. 관심 있으시면 연락 주세요.";
            } elseif ($type === 'sale') {
                $content .= "위치 좋고 학군 좋은 지역입니다. 오픈하우스 가능합니다. 에이전트 통해 연락 주세요.";
            } else {
                $content .= "깨끗하게 생활하시는 분 구합니다. 유틸리티 별도입니다. 관심 있으시면 연락 주세요.";
            }

            $rows[] = [
                'user_id'        => $userIds[array_rand($userIds)],
                'title'          => $title,
                'content'        => $content,
                'type'           => $type,
                'property_type'  => $propertyType,
                'price'          => $price,
                'deposit'        => $deposit,
                'images'         => null,
                'address'        => $addresses[array_rand($addresses)],
                'city'           => $city['city'],
                'state'          => $city['state'],
                'zipcode'        => $city['zips'][array_rand($city['zips'])],
                'lat'            => round($city['lat'] + rand(-300, 300) / 10000, 7),
                'lng'            => round($city['lng'] + rand(-300, 300) / 10000, 7),
                'bedrooms'       => $bedrooms,
                'bathrooms'      => $bathrooms,
                'sqft'           => $sqft,
                'is_active'      => rand(0, 100) > 10,
                'view_count'     => rand(10, 500),
                'contact_phone'  => '(' . rand(200, 999) . ') ' . rand(200, 999) . '-' . rand(1000, 9999),
                'contact_email'  => 'realestate' . rand(1, 99) . '@example.com',
                'created_at'     => $now->copy()->subDays(rand(0, 60))->subHours(rand(0, 23)),
                'updated_at'     => $now,
            ];
        }

        foreach (array_chunk($rows, 50) as $chunk) {
            RealEstateListing::insert($chunk);
        }

        $this->command->info('RealEstateSeeder: 300 real estate listings created');
    }
}
