<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class RealEstateDummySeeder extends Seeder
{
    public function run(): void
    {
        $userIds = DB::table('users')->pluck('id')->toArray();
        if (empty($userIds)) {
            $this->command->error('users 테이블에 데이터가 없습니다. FakeUsersSeeder를 먼저 실행하세요.');
            return;
        }

        $this->command->info('부동산 300개 생성 중...');

        // ── 한인 밀집 지역 주소 데이터 ──
        $regionData = [
            'Los Angeles' => [
                'addresses' => ['3000 W Olympic Blvd, Los Angeles, CA 90006', '621 S Western Ave, Los Angeles, CA 90005', '3500 W 6th St, Los Angeles, CA 90020', '4001 Wilshire Blvd, Los Angeles, CA 90010', '2800 W 8th St, Los Angeles, CA 90005', '3200 Wilshire Blvd, Los Angeles, CA 90010', '450 S Western Ave, Los Angeles, CA 90020'],
                'lat' => [34.0530, 34.0620], 'lng' => [-118.3100, -118.2900],
            ],
            'New York' => [
                'addresses' => ['149-06 41st Ave, Flushing, NY 11355', '32 W 32nd St, New York, NY 10001', '150-28 Northern Blvd, Flushing, NY 11354', '136-20 38th Ave, Flushing, NY 11354', '35-20 Farrington St, Flushing, NY 11354'],
                'lat' => [40.7580, 40.7630], 'lng' => [-73.8300, -73.8200],
            ],
            'Atlanta' => [
                'addresses' => ['5302 Buford Hwy, Doraville, GA 30340', '3242 Steve Reynolds Blvd, Duluth, GA 30096', '2550 Pleasant Hill Rd, Duluth, GA 30096', '6035 Peachtree Rd, Doraville, GA 30360'],
                'lat' => [33.8900, 33.9200], 'lng' => [-84.2800, -84.2500],
            ],
            'Chicago' => [
                'addresses' => ['4747 N Western Ave, Chicago, IL 60625', '3346 W Bryn Mawr Ave, Chicago, IL 60659', '5000 N Lincoln Ave, Chicago, IL 60625', '3500 N Milwaukee Ave, Chicago, IL 60641'],
                'lat' => [41.9600, 41.9800], 'lng' => [-87.6900, -87.6700],
            ],
            'Seattle' => [
                'addresses' => ['2320 S Jackson St, Seattle, WA 98144', '1032 S Jackson St, Seattle, WA 98104', '520 6th Ave S, Seattle, WA 98104'],
                'lat' => [47.5990, 47.6020], 'lng' => [-122.3200, -122.3100],
            ],
            'Dallas' => [
                'addresses' => ['2625 Old Denton Rd, Carrollton, TX 75007', '1100 Royal Ln, Dallas, TX 75229', '2540 Royal Ln, Dallas, TX 75229', '11311 Harry Hines Blvd, Dallas, TX 75229'],
                'lat' => [32.8600, 32.8800], 'lng' => [-96.8700, -96.8500],
            ],
            'Houston' => [
                'addresses' => ['1302 Blalock Rd, Houston, TX 77055', '9896 Bellaire Blvd, Houston, TX 77036', '1005 Blalock Rd, Houston, TX 77055'],
                'lat' => [29.7700, 29.7900], 'lng' => [-95.5200, -95.5000],
            ],
            'San Francisco' => [
                'addresses' => ['2370 Noriega St, San Francisco, CA 94122', '1531 Clement St, San Francisco, CA 94118', '3439 Geary Blvd, San Francisco, CA 94118'],
                'lat' => [37.7530, 37.7600], 'lng' => [-122.4800, -122.4600],
            ],
            'San Jose' => [
                'addresses' => ['3150 El Camino Real, Santa Clara, CA 95051', '1530 Hamilton Ave, San Jose, CA 95125', '2855 Stevens Creek Blvd, San Jose, CA 95128'],
                'lat' => [37.3380, 37.3500], 'lng' => [-121.9500, -121.9300],
            ],
            'Virginia' => [
                'addresses' => ['7048 Spring Garden Dr, Annandale, VA 22003', '8515 Lee Hwy, Fairfax, VA 22031', '3217 Columbia Pike, Arlington, VA 22204'],
                'lat' => [38.8300, 38.8500], 'lng' => [-77.2100, -77.1900],
            ],
            'New Jersey' => [
                'addresses' => ['1585 Palisade Ave, Fort Lee, NJ 07024', '300 Broad Ave, Palisades Park, NJ 07650', '201 Main St, Fort Lee, NJ 07024'],
                'lat' => [40.8500, 40.8700], 'lng' => [-73.9800, -73.9600],
            ],
        ];

        $regions = array_keys($regionData);
        $petPolicies = ['가능', '불가', '협의'];
        $now = Carbon::now();

        // ── 렌트 제목/설명 템플릿 ──
        $rentTemplates = [
            ['title' => '{bed}BR/{bath}BA 코리아타운 ${price}/mo', 'desc' => '코리아타운 근처 {bed}베드/{bath}배쓰 아파트. 주방 리모델링 완료. 세탁기/건조기 건물 내 있음. 주차 1대 포함.'],
            ['title' => '{bed}BR 풀옵션 하이라이즈 ${price}', 'desc' => '하이라이즈 아파트 {bed}BR/{bath}BA. 수영장, 헬스장, 컨시어지 서비스 포함. 전망 좋���.'],
            ['title' => '넓은 {bed}BR 아파트 ${price}/월', 'desc' => '밝고 넓은 {bed}BR/{bath}BA 아파트. 자연광 좋고 조용한 동네. 근처 한인마트 도보 가능.'],
            ['title' => '{bed}BR 깨끗한 아파트 급구 ${price}', 'desc' => '깨끗하게 관리된 {bed}BR/{bath}BA 아파트. 새 페인트. 가전제품 포함. 즉시 입주 가능.'],
            ['title' => '한인타운 {bed}BR 월 ${price}', 'desc' => '한인타운 중심부 {bed}BR/{bath}BA. 대중교통 편리. 주변 편의시설 많음. 1년 리스.'],
            ['title' => '학군 좋은 {bed}BR/${price}', 'desc' => '학군 우수 지역 {bed}BR/{bath}BA. 공원 근접. 안전한 주택가. 가족 추���.'],
            ['title' => '스튜디오 ${price}/월 유틸리티 포함', 'desc' => '아담한 스튜디오 아파트. 유틸리티 포함. 가구 옵션 가능. 싱글/커플 적합.'],
            ['title' => '{bed}BR 타운하우스 ${price}/mo', 'desc' => '2층 타운하우스 {bed}BR/{bath}BA. 전용 차고 있음. 조용한 주택단지.'],
        ];

        // ── 매매 제목/설명 템플릿 ──
        $saleTemplates = [
            ['title' => '{bed}BR/{bath}BA 단독주택 ${price}', 'desc' => '한인 밀집 지역 단독주택 {bed}BR/{bath}BA. 마당 있음. 리모델링 완료. HOA 없음.'],
            ['title' => '코리아타운 콘도 ${price}', 'desc' => '코리아타운 {bed}BR/{bath}BA 콘도. 주차 2대. 발코니. 보안 게이트.'],
            ['title' => '신축 타운홈 ${price}', 'desc' => '2024년 신축 타운홈 {bed}BR/{bath}BA. 최신 인테리어. 에너지 효율 우수.'],
            ['title' => '투자용 듀플렉스 ${price}', 'desc' => '투자용 듀플렉스. 각 유닛 {bed}BR/{bath}BA. 현재 렌트 중. 수익률 좋음.'],
            ['title' => '학군 좋은 주택 ${price}', 'desc' => '최고 학군 지역 {bed}BR/{bath}BA 주택. 넓은 마당. 리모델링 주방.'],
        ];

        // ── 룸메이트 제목/설명 템플릿 ──
        $roommateTemplates = [
            ['title' => '룸메이트 구합니다 ${price}/월', 'desc' => '{bed}BR 아파트에서 방 1개 쉐어합니다. 화장실 공용. 유틸리티 포함. 여성/남성 선호.'],
            ['title' => '마스터룸 쉐어 ${price}', 'desc' => '마스터룸 (전용 화장실) 쉐어합니다. 넓고 깨끗. 한인 선호.'],
            ['title' => '깔끔한 방 쉐어 ${price}/월', 'desc' => '깨끗한 아파트에서 방 하나 쉐어합니다. 가구 완비. 주차 가능. 한인 학생/직장인 환영.'],
            ['title' => '퍼니쉬드 룸 ${price}/월', 'desc' => '가구 완비된 방. 침대, 책상, 옷장 포함. 인터넷/유틸 포함. 즉시 입주 가능.'],
        ];

        $rows = [];

        for ($i = 0; $i < 300; $i++) {
            // 타입: 렌트(60%), 매매(25%), 룸메이트(15%)
            $typeRand = rand(1, 100);
            if ($typeRand <= 60) {
                $type = '렌���';
            } elseif ($typeRand <= 85) {
                $type = '매매';
            } else {
                $type = '룸메이트';
            }

            $regionKey = $regions[array_rand($regions)];
            $rData = $regionData[$regionKey];
            $address = $rData['addresses'][array_rand($rData['addresses'])];
            $lat = round($rData['lat'][0] + (mt_rand() / mt_getrandmax()) * ($rData['lat'][1] - $rData['lat'][0]), 7);
            $lng = round($rData['lng'][0] + (mt_rand() / mt_getrandmax()) * ($rData['lng'][1] - $rData['lng'][0]), 7);

            if ($type === '렌트') {
                $bed = rand(0, 3); // 0 = studio
                $bath = max(1, $bed);
                $price = $bed === 0 ? rand(800, 1800) : rand(1200, 4000);
                $deposit = $price; // 보증금 = 1개월치
                $sqft = $bed === 0 ? rand(300, 600) : rand(500, 1800);
                $template = $rentTemplates[array_rand($rentTemplates)];
                $title = str_replace(['{bed}', '{bath}', '{price}'], [$bed === 0 ? 'Studio' : (string)$bed, (string)$bath, number_format($price)], $template['title']);
                $desc = str_replace(['{bed}', '{bath}', '{price}'], [$bed === 0 ? 'Studio' : (string)$bed, (string)$bath, number_format($price)], $template['desc']);
                $moveIn = $now->copy()->addDays(rand(1, 60))->format('Y-m-d');
            } elseif ($type === '매매') {
                $bed = rand(2, 5);
                $bath = rand(1, 3);
                $priceK = rand(200, 1500); // $200K ~ $1.5M
                $price = $priceK * 1000;
                $deposit = null;
                $sqft = rand(800, 3500);
                $template = $saleTemplates[array_rand($saleTemplates)];
                $priceStr = $priceK >= 1000 ? number_format($priceK / 1000, 1) . 'M' : $priceK . 'K';
                $title = str_replace(['{bed}', '{bath}', '{price}'], [(string)$bed, (string)$bath, $priceStr], $template['title']);
                $desc = str_replace(['{bed}', '{bath}', '{price}'], [(string)$bed, (string)$bath, $priceStr], $template['desc']);
                $moveIn = null;
            } else { // 룸메이트
                $bed = rand(2, 4);
                $bath = rand(1, 2);
                $price = rand(500, 1200);
                $deposit = $price;
                $sqft = null;
                $template = $roommateTemplates[array_rand($roommateTemplates)];
                $title = str_replace(['{bed}', '{bath}', '{price}'], [(string)$bed, (string)$bath, number_format($price)], $template['title']);
                $desc = str_replace(['{bed}', '{bath}', '{price}'], [(string)$bed, (string)$bath, number_format($price)], $template['desc']);
                $moveIn = $now->copy()->addDays(rand(1, 30))->format('Y-m-d');
            }

            $phone = '(' . rand(200, 999) . ') ' . rand(200, 999) . '-' . str_pad(rand(0, 9999), 4, '0', STR_PAD_LEFT);
            $email = 'realestate' . rand(100, 999) . '@' . ['gmail.com', 'yahoo.com', 'naver.com'][array_rand(['gmail.com', 'yahoo.com', 'naver.com'])];

            $daysAgo = rand(0, 90);
            $hour = rand(7, 23);
            $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute(rand(0, 59))->setSecond(rand(0, 59));

            $statusRand = rand(1, 100);
            $status = $statusRand <= 80 ? 'active' : 'closed';

            $rows[] = [
                'user_id'     => $userIds[array_rand($userIds)],
                'title'       => $title,
                'description' => $desc . "\n\n관심 있으시면 연락 주세요. 투어 가능합니다.",
                'type'        => $type,
                'price'       => $price,
                'deposit'     => $deposit,
                'address'     => $address,
                'region'      => $regionKey,
                'latitude'    => $lat,
                'longitude'   => $lng,
                'bedrooms'    => $type === '룸메이트' ? 1 : ($bed === 0 ? 0 : $bed),
                'bathrooms'   => $bath,
                'sqft'        => $sqft,
                'photos'      => null,
                'move_in_date' => $moveIn,
                'pet_policy'  => $petPolicies[array_rand($petPolicies)],
                'phone'       => $phone,
                'email'       => $email,
                'is_pinned'   => false,
                'view_count'  => rand(30, 2000),
                'status'      => $status,
                'created_at'  => $createdAt,
                'updated_at'  => $createdAt,
            ];
        }

        // 50개씩 chunk insert
        foreach (array_chunk($rows, 50) as $chunk) {
            DB::table('real_estate_listings')->insert($chunk);
        }

        $this->command->info('부동산 300개 생��� 완료!');
    }
}
