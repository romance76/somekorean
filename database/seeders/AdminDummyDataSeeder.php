<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class AdminDummyDataSeeder extends Seeder
{
    public function run(): void
    {
        $this->seedSiteSettings();
        $this->seedPayments();
        $this->seedBanners();
        $this->seedRides();
        $this->seedGroupBuys();
        $this->seedChatRoomsAndMessages();
        $this->seedBusinesses();
        $this->seedElderSettings();
        $this->seedDriverProfiles();
    }

    private function getUserIds(): array
    {
        $userIds = DB::table('users')->pluck('id')->toArray();
        return $userIds;
    }

    private function seedSiteSettings(): void
    {
        if (DB::table('site_settings')->count() === 0) {
            $defaults = [
                ['key' => 'site_name',    'value' => 'SomeKorean',                   'created_at' => now(), 'updated_at' => now()],
                ['key' => 'site_subtitle','value' => '미국 한인 커뮤니티',              'created_at' => now(), 'updated_at' => now()],
                ['key' => 'company_name', 'value' => 'SomeKorean Inc.',               'created_at' => now(), 'updated_at' => now()],
                ['key' => 'address',      'value' => 'Los Angeles, CA, USA',          'created_at' => now(), 'updated_at' => now()],
                ['key' => 'email',        'value' => 'admin@somekorean.com',          'created_at' => now(), 'updated_at' => now()],
            ];
            DB::table('site_settings')->insert($defaults);
        }
    }

    private function seedPayments(): void
    {
        if (DB::table('payments')->count() === 0) {
            $types = [
                '포인트충전' => [
                    'items'   => ['포인트 1,000P 충전', '포인트 3,000P 충전', '포인트 5,000P 충전', '포인트 10,000P 충전'],
                    'amounts' => [5.00, 10.00, 15.00, 25.00],
                ],
                '프리미엄'   => [
                    'items'   => ['프리미엄 회원 1개월', '프리미엄 회원 3개월', '프리미엄 회원 6개월', '프리미엄 회원 1년'],
                    'amounts' => [9.99, 24.99, 44.99, 79.99],
                ],
                '공동구매'   => [
                    'items'   => ['LA 갈비세트 공동구매', '한우 소고기 공동구매', '제주 감귤 공동구매', '유기농 쌀 20kg 공동구매'],
                    'amounts' => [35.00, 58.00, 22.00, 45.00],
                ],
                '업소등록'   => [
                    'items'   => ['업소 기본 등록 (1개월)', '업소 프리미엄 등록 (3개월)', '업소 프리미엄 등록 (6개월)', '업소 TOP 광고 (1개월)'],
                    'amounts' => [29.00, 75.00, 130.00, 150.00],
                ],
            ];

            $cardBrands = ['visa', 'mastercard', 'amex', 'discover'];
            $methods    = ['card', 'card', 'card', 'apple_pay', 'google_pay'];

            // Weighted statuses: 80% success, 10% failed, 10% refunded
            $statusPool = array_merge(
                array_fill(0, 16, 'success'),
                array_fill(0, 2,  'failed'),
                array_fill(0, 2,  'refunded')
            );

            $typeKeys = array_keys($types);
            $now      = Carbon::now();
            $rows     = [];

            $userIds = $this->getUserIds();
            if (empty($userIds)) return;

            for ($i = 0; $i < 30; $i++) {
                $typeKey = $typeKeys[$i % count($typeKeys)];
                $typeKey   = $typeKeys[array_rand($typeKeys)];
                $typeData  = $types[$typeKey];
                $itemIndex = array_rand($typeData['items']);
                $itemName  = $typeData['items'][$itemIndex];
                $amount    = $typeData['amounts'][$itemIndex];

                $status    = $statusPool[$i % count($statusPool)];
                $method    = $methods[array_rand($methods)];
                $cardBrand = ($method === 'card') ? $cardBrands[array_rand($cardBrands)] : null;
                $cardLast4 = ($method === 'card') ? str_pad((string)rand(1000, 9999), 4, '0', STR_PAD_LEFT) : null;

                $daysAgo   = rand(1, 180);
                $createdAt = $now->copy()->subDays($daysAgo)->subHours(rand(0, 23))->subMinutes(rand(0, 59));
                $paidAt    = ($status === 'success' || $status === 'refunded') ? $createdAt->copy()->addSeconds(rand(5, 60)) : null;

                $userId        = $userIds[array_rand($userIds)];
                $transactionId = 'TXN-' . strtoupper(substr(md5($i . $createdAt->timestamp . rand()), 0, 12));
                $stripeId      = 'pi_' . bin2hex(random_bytes(12));

                $rows[] = [
                    'user_id'          => $userId,
                    'transaction_id'   => $transactionId,
                    'type'             => $typeKey,
                    'item_name'        => $itemName,
                    'amount'           => $amount,
                    'currency'         => 'USD',
                    'payment_method'   => $method,
                    'card_brand'       => $cardBrand,
                    'card_last4'       => $cardLast4,
                    'status'           => $status,
                    'stripe_payment_id'=> $stripeId,
                    'memo'             => $status === 'refunded' ? '고객 요청으로 환불 처리' : ($status === 'failed' ? '카드 승인 실패' : null),
                    'paid_at'          => $paidAt,
                    'created_at'       => $createdAt,
                    'updated_at'       => $createdAt,
                ];
            }

            DB::table('payments')->insert($rows);
        }
    }

    private function seedBanners(): void
    {
        if (DB::table('banners')->count() === 0) {
            $now = Carbon::now();

            $banners = [
                [
                    'name'        => '메인 상단 배너 - 한인 커뮤니티 소개',
                    'position'    => '메인상단',
                    'image_url'   => '/storage/banners/main_top_banner.jpg',
                    'link_url'    => '/about',
                    'new_tab'     => false,
                    'start_at'    => $now->copy()->startOfMonth()->toDateString(),
                    'end_at'      => $now->copy()->addMonths(3)->endOfMonth()->toDateString(),
                    'order'       => 1,
                    'active'      => true,
                    'advertiser'  => 'SomeKorean 자체',
                    'amount'      => 0.00,
                    'clicks'      => rand(120, 850),
                    'impressions' => rand(3000, 15000),
                    'memo'        => '메인 페이지 상단 히어로 배너. 신규 회원 유입용.',
                    'created_at'  => $now->copy()->subDays(60),
                    'updated_at'  => $now->copy()->subDays(5),
                ],
                [
                    'name'        => 'LA 한인마트 광고 배너',
                    'position'    => '메인중간',
                    'image_url'   => '/storage/banners/la_hmart_banner.jpg',
                    'link_url'    => 'https://www.hmart.com',
                    'new_tab'     => true,
                    'start_at'    => $now->copy()->subDays(30)->toDateString(),
                    'end_at'      => $now->copy()->addDays(60)->toDateString(),
                    'order'       => 2,
                    'active'      => true,
                    'advertiser'  => 'H마트 LA점',
                    'amount'      => 350.00,
                    'clicks'      => rand(200, 1200),
                    'impressions' => rand(5000, 25000),
                    'memo'        => '3개월 계약 광고. 담당자: 김민준 213-555-0192.',
                    'created_at'  => $now->copy()->subDays(30),
                    'updated_at'  => $now->copy()->subDays(1),
                ],
                [
                    'name'        => '한인 부동산 사이드 배너',
                    'position'    => '사이드',
                    'image_url'   => '/storage/banners/realty_side_banner.jpg',
                    'link_url'    => '/businesses?category=부동산',
                    'new_tab'     => false,
                    'start_at'    => $now->copy()->subDays(15)->toDateString(),
                    'end_at'      => $now->copy()->addDays(75)->toDateString(),
                    'order'       => 3,
                    'active'      => true,
                    'advertiser'  => 'Korea Real Estate Group',
                    'amount'      => 200.00,
                    'clicks'      => rand(80, 450),
                    'impressions' => rand(2000, 10000),
                    'memo'        => 'LA/OC 지역 한인 부동산 업체 광고. 사이드바 고정 노출.',
                    'created_at'  => $now->copy()->subDays(15),
                    'updated_at'  => $now->copy()->subDays(2),
                ],
                [
                    'name'        => '추석 특별 이벤트 팝업 배너',
                    'position'    => '팝업',
                    'image_url'   => '/storage/banners/chuseok_popup_banner.jpg',
                    'link_url'    => '/events/chuseok-2026',
                    'new_tab'     => false,
                    'start_at'    => $now->copy()->addDays(170)->toDateString(),
                    'end_at'      => $now->copy()->addDays(185)->toDateString(),
                    'order'       => 4,
                    'active'      => false,
                    'advertiser'  => 'SomeKorean 자체',
                    'amount'      => 0.00,
                    'clicks'      => 0,
                    'impressions' => 0,
                    'memo'        => '추석 이벤트 팝업. 기간 외에는 비활성 상태 유지.',
                    'created_at'  => $now->copy()->subDays(3),
                    'updated_at'  => $now->copy()->subDays(3),
                ],
            ];

            DB::table('banners')->insert($banners);
        }
    }

    private function seedRides(): void
    {
        if (DB::table('rides')->count() === 0) {
            $userIds = $this->getUserIds();
            if (count($userIds) < 2) return;

            $now = Carbon::now();
            $statuses = ['pending', 'accepted', 'in_progress', 'completed', 'completed', 'completed', 'completed', 'cancelled', 'pending', 'completed'];
            $pickups = [
                'Koreatown, LA', 'Fullerton, CA', 'Garden Grove, CA', 'Irvine, CA', 'Torrance, CA',
                'Buena Park, CA', 'Glendale, CA', 'Cerritos, CA', 'Rowland Heights, CA', 'Palisades Park, NJ',
            ];
            $dropoffs = [
                'LAX Airport', 'Downtown LA', 'H마트 Irvine', 'UCLA', 'Santa Monica',
                'Ontario Airport', 'Disneyland', 'Long Beach', 'Pasadena', 'Fort Lee, NJ',
            ];

            $rows = [];
            for ($i = 0; $i < 10; $i++) {
                $passengerId = $userIds[array_rand($userIds)];
                // Pick a different user as driver
                $driverPool = array_diff($userIds, [$passengerId]);
                $driverId = !empty($driverPool) ? $driverPool[array_rand($driverPool)] : $passengerId;

                $status = $statuses[$i];
                $daysAgo = rand(0, 30);
                $createdAt = $now->copy()->subDays($daysAgo)->subHours(rand(0, 12));
                $fare = round(rand(800, 6500) / 100, 2); // $8.00 - $65.00

                $completedAt = ($status === 'completed') ? $createdAt->copy()->addMinutes(rand(15, 90)) : null;
                $acceptedAt = in_array($status, ['accepted', 'in_progress', 'completed']) ? $createdAt->copy()->addMinutes(rand(1, 10)) : null;

                $rows[] = [
                    'passenger_id'  => $passengerId,
                    'driver_id'     => in_array($status, ['accepted', 'in_progress', 'completed']) ? $driverId : null,
                    'pickup'        => $pickups[$i],
                    'dropoff'       => $dropoffs[$i],
                    'fare'          => $fare,
                    'status'        => $status,
                    'pickup_lat'    => 33.9 + (rand(0, 100) / 1000),
                    'pickup_lng'    => -118.3 + (rand(0, 100) / 1000),
                    'dropoff_lat'   => 33.9 + (rand(0, 100) / 1000),
                    'dropoff_lng'   => -118.3 + (rand(0, 100) / 1000),
                    'distance'      => round(rand(20, 450) / 10, 1),
                    'notes'         => $i % 3 === 0 ? '짐이 좀 많습니다' : null,
                    'accepted_at'   => $acceptedAt,
                    'completed_at'  => $completedAt,
                    'created_at'    => $createdAt,
                    'updated_at'    => $completedAt ?? $acceptedAt ?? $createdAt,
                ];
            }

            DB::table('rides')->insert($rows);
        }
    }

    private function seedGroupBuys(): void
    {
        if (DB::table('group_buys')->count() === 0) {
            $userIds = $this->getUserIds();
            if (empty($userIds)) return;

            $now = Carbon::now();

            $items = [
                [
                    'title'            => 'LA 갈비세트 공동구매',
                    'description'      => '프리미엄 LA 갈비 5lb 세트. 최소 10명 모이면 개당 $35에 구매 가능합니다.',
                    'price'            => 35.00,
                    'min_participants' => 10,
                    'max_participants' => 30,
                    'category'         => '식품',
                    'status'           => 'open',
                    'deadline'         => $now->copy()->addDays(7)->toDateTimeString(),
                ],
                [
                    'title'            => '유기농 쌀 20kg 공동구매',
                    'description'      => '캘리포니아산 유기농 쌀 20kg. 대량 구매 할인가로 제공합니다.',
                    'price'            => 45.00,
                    'min_participants' => 15,
                    'max_participants' => 50,
                    'category'         => '식품',
                    'status'           => 'open',
                    'deadline'         => $now->copy()->addDays(14)->toDateTimeString(),
                ],
                [
                    'title'            => '김치냉장고 공동구매',
                    'description'      => '딤채 김치냉장고 최신형. 공동구매 시 $200 할인!',
                    'price'            => 899.00,
                    'min_participants' => 5,
                    'max_participants' => 20,
                    'category'         => '가전',
                    'status'           => 'open',
                    'deadline'         => $now->copy()->addDays(21)->toDateTimeString(),
                ],
                [
                    'title'            => '제주 감귤 박스 공동구매',
                    'description'      => '제주 직송 감귤 10kg 박스. 신선도 보장!',
                    'price'            => 22.00,
                    'min_participants' => 20,
                    'max_participants' => 100,
                    'category'         => '식품',
                    'status'           => 'closed',
                    'deadline'         => $now->copy()->subDays(3)->toDateTimeString(),
                ],
                [
                    'title'            => '한국어 교재 세트 공동구매',
                    'description'      => '어린이 한국어 학습 교재 세트 (3권). 한글학교 교재용.',
                    'price'            => 28.00,
                    'min_participants' => 8,
                    'max_participants' => 40,
                    'category'         => '교육',
                    'status'           => 'pending',
                    'deadline'         => $now->copy()->addDays(10)->toDateTimeString(),
                ],
                [
                    'title'            => '삼성 Galaxy S26 케이스 공동구매',
                    'description'      => '삼성 Galaxy S26 프리미엄 케이스 대량 주문 할인.',
                    'price'            => 15.00,
                    'min_participants' => 10,
                    'max_participants' => 50,
                    'category'         => '전자기기',
                    'status'           => 'open',
                    'deadline'         => $now->copy()->addDays(5)->toDateTimeString(),
                ],
            ];

            $rows = [];
            foreach ($items as $i => $item) {
                $daysAgo = rand(1, 20);
                $createdAt = $now->copy()->subDays($daysAgo);
                $rows[] = array_merge($item, [
                    'user_id'    => $userIds[array_rand($userIds)],
                    'created_at' => $createdAt,
                    'updated_at' => $createdAt,
                ]);
            }

            DB::table('group_buys')->insert($rows);
        }
    }

    private function seedChatRoomsAndMessages(): void
    {
        if (DB::table('chat_rooms')->count() === 0) {
            $userIds = $this->getUserIds();
            if (empty($userIds)) return;

            $now = Carbon::now();

            $rooms = [
                [
                    'name'        => '자유잡담',
                    'slug'        => 'free-chat',
                    'description' => '자유롭게 이야기하는 채팅방입니다.',
                    'type'        => 'public',
                    'max_members' => 200,
                    'created_by'  => $userIds[0],
                    'created_at'  => $now->copy()->subDays(60),
                    'updated_at'  => $now->copy()->subDays(1),
                ],
                [
                    'name'        => 'LA 한인 정보공유',
                    'slug'        => 'la-info',
                    'description' => 'LA 지역 한인 생활 정보를 공유하는 방입니다.',
                    'type'        => 'public',
                    'max_members' => 150,
                    'created_by'  => $userIds[0],
                    'created_at'  => $now->copy()->subDays(45),
                    'updated_at'  => $now->copy()->subHours(3),
                ],
                [
                    'name'        => '맛집 추천',
                    'slug'        => 'food-recs',
                    'description' => '한인 맛집 추천 채팅방. 맛집 정보를 공유해주세요!',
                    'type'        => 'public',
                    'max_members' => 100,
                    'created_by'  => count($userIds) > 1 ? $userIds[1] : $userIds[0],
                    'created_at'  => $now->copy()->subDays(30),
                    'updated_at'  => $now->copy()->subHours(6),
                ],
                [
                    'name'        => '부동산/렌트 상담',
                    'slug'        => 'real-estate',
                    'description' => '부동산, 렌트, 집 구하기 관련 정보 교환방.',
                    'type'        => 'public',
                    'max_members' => 100,
                    'created_by'  => count($userIds) > 2 ? $userIds[2] : $userIds[0],
                    'created_at'  => $now->copy()->subDays(20),
                    'updated_at'  => $now->copy()->subDays(2),
                ],
                [
                    'name'        => '관리자 전용',
                    'slug'        => 'admin-only',
                    'description' => '관리자 전용 비공개 채팅방.',
                    'type'        => 'private',
                    'max_members' => 10,
                    'created_by'  => $userIds[0],
                    'created_at'  => $now->copy()->subDays(90),
                    'updated_at'  => $now->copy()->subDays(1),
                ],
            ];

            DB::table('chat_rooms')->insert($rooms);
        }

        // Seed chat messages
        if (DB::table('chat_messages')->count() === 0) {
            $userIds = $this->getUserIds();
            if (empty($userIds)) return;

            $roomIds = DB::table('chat_rooms')->pluck('id')->toArray();
            if (empty($roomIds)) return;

            $now = Carbon::now();

            $sampleMessages = [
                '안녕하세요! 반갑습니다~',
                '오늘 날씨 너무 좋네요',
                'LA 한인타운에 새로 생긴 식당 가보셨어요?',
                '혹시 좋은 한국 마트 추천해주실 분?',
                '이번 주말에 뭐 하세요?',
                '감사합니다 좋은 정보네요!',
                '저도 궁금했는데 감사해요',
                'H마트 세일 시작했대요',
                '렌트비가 너무 올랐어요...',
                '다들 건강하세요!',
                '한국 음식 배달 앱 추천 좀 해주세요',
                '이민 서류 어디서 처리하셨어요?',
                '주말에 한인회관 행사 있대요',
                '한국어 학원 추천 부탁드려요',
                '차 보험 어디가 저렴한가요?',
                '오렌지카운티 쪽에 사시는 분 계세요?',
                '한인 타운 맛집 리스트 공유합니다!',
                '이번 달 모임 날짜가 언제인가요?',
                '좋은 하루 되세요 ^^',
                '정보 감사합니다~',
            ];

            $rows = [];
            for ($i = 0; $i < 20; $i++) {
                $hoursAgo = rand(0, 168); // within last week
                $createdAt = $now->copy()->subHours($hoursAgo)->subMinutes(rand(0, 59));
                $rows[] = [
                    'chat_room_id' => $roomIds[array_rand($roomIds)],
                    'user_id'      => $userIds[array_rand($userIds)],
                    'message'      => $sampleMessages[$i],
                    'type'         => 'text',
                    'created_at'   => $createdAt,
                    'updated_at'   => $createdAt,
                ];
            }

            DB::table('chat_messages')->insert($rows);
        }
    }

    private function seedBusinesses(): void
    {
        if (DB::table('businesses')->count() === 0) {
            $userIds = $this->getUserIds();
            if (empty($userIds)) return;

            $now = Carbon::now();

            $businesses = [
                [
                    'name'         => '서울가든',
                    'english_name' => 'Seoul Garden',
                    'category'     => '음식점',
                    'owner_name'   => '김철수',
                    'phone'        => '213-555-0101',
                    'email'        => 'info@seoulgarden.com',
                    'website'      => 'https://seoulgarden.com',
                    'address'      => '3456 W Olympic Blvd, Los Angeles, CA 90019',
                    'description'  => '정통 한식 전문점. 갈비, 불고기, 냉면 등 다양한 메뉴를 제공합니다.',
                    'hours'        => '월-토 11:00-22:00, 일 12:00-21:00',
                    'status'       => 'active',
                    'verified'     => true,
                ],
                [
                    'name'         => '한빛 부동산',
                    'english_name' => 'Hanbit Realty',
                    'category'     => '부동산',
                    'owner_name'   => '이영희',
                    'phone'        => '213-555-0202',
                    'email'        => 'contact@hanbitrealty.com',
                    'website'      => 'https://hanbitrealty.com',
                    'address'      => '621 S Western Ave #200, Los Angeles, CA 90005',
                    'description'  => 'LA/OC 지역 한인 부동산 전문. 주거용/상업용 매매 및 임대.',
                    'hours'        => '월-금 9:00-18:00, 토 10:00-15:00',
                    'status'       => 'active',
                    'verified'     => true,
                ],
                [
                    'name'         => '뷰티 서울',
                    'english_name' => 'Beauty Seoul',
                    'category'     => '미용실',
                    'owner_name'   => '박미선',
                    'phone'        => '213-555-0303',
                    'email'        => 'beautyseoul@gmail.com',
                    'website'      => null,
                    'address'      => '928 S Western Ave, Los Angeles, CA 90006',
                    'description'  => '한인타운 최고의 미용실. 커트, 펌, 염색, 네일 전문.',
                    'hours'        => '화-토 10:00-19:00',
                    'status'       => 'active',
                    'verified'     => true,
                ],
                [
                    'name'         => '한국 자동차 정비',
                    'english_name' => 'Korea Auto Service',
                    'category'     => '자동차',
                    'owner_name'   => '최동현',
                    'phone'        => '213-555-0404',
                    'email'        => 'koreauto@gmail.com',
                    'website'      => null,
                    'address'      => '1250 S Vermont Ave, Los Angeles, CA 90006',
                    'description'  => '한인 자동차 정비 전문. 엔진, 브레이크, 오일 교환 등.',
                    'hours'        => '월-금 8:00-18:00, 토 9:00-14:00',
                    'status'       => 'active',
                    'verified'     => false,
                ],
                [
                    'name'         => '동방 보험',
                    'english_name' => 'Dongbang Insurance',
                    'category'     => '보험',
                    'owner_name'   => '정수진',
                    'phone'        => '213-555-0505',
                    'email'        => 'dongbang.ins@gmail.com',
                    'website'      => 'https://dongbanginsurance.com',
                    'address'      => '3200 Wilshire Blvd #500, Los Angeles, CA 90010',
                    'description'  => '자동차, 건강, 생명, 비즈니스 보험 전문 에이전시.',
                    'hours'        => '월-금 9:00-17:30',
                    'status'       => 'active',
                    'verified'     => true,
                ],
                [
                    'name'         => '새소망 교회',
                    'english_name' => 'New Hope Church',
                    'category'     => '종교',
                    'owner_name'   => '김목사',
                    'phone'        => '213-555-0606',
                    'email'        => 'newhope@church.org',
                    'website'      => 'https://newhopechurch.org',
                    'address'      => '4500 W 3rd St, Los Angeles, CA 90020',
                    'description'  => '한인 교회. 주일예배, 수요예배, 금요기도회.',
                    'hours'        => '일 9:00-13:00, 수 19:00-21:00, 금 20:00-22:00',
                    'status'       => 'active',
                    'verified'     => false,
                ],
                [
                    'name'         => '맛나 분식',
                    'english_name' => 'Mattna Bunsik',
                    'category'     => '음식점',
                    'owner_name'   => '한지민',
                    'phone'        => '714-555-0707',
                    'email'        => 'mattna.bunsik@gmail.com',
                    'website'      => null,
                    'address'      => '9872 Garden Grove Blvd, Garden Grove, CA 92844',
                    'description'  => '떡볶이, 순대, 튀김, 김밥 등 한국 분식 전문점. 신규 오픈!',
                    'hours'        => '매일 11:00-21:00',
                    'status'       => 'pending',
                    'verified'     => false,
                ],
                [
                    'name'         => '코리아 로펌',
                    'english_name' => 'Korea Law Firm',
                    'category'     => '법률',
                    'owner_name'   => '윤변호사',
                    'phone'        => '213-555-0808',
                    'email'        => 'korealawfirm@gmail.com',
                    'website'      => 'https://korealawfirm.com',
                    'address'      => '3435 Wilshire Blvd #1200, Los Angeles, CA 90010',
                    'description'  => '이민법, 부동산법, 사업법 전문. 한국어 상담 가능.',
                    'hours'        => '월-금 9:00-18:00',
                    'status'       => 'pending',
                    'verified'     => false,
                ],
            ];

            $rows = [];
            foreach ($businesses as $i => $biz) {
                $daysAgo = rand(1, 90);
                $createdAt = $now->copy()->subDays($daysAgo);
                // is_approved mirrors the status field: active = approved, pending = not yet approved
                $isApproved = ($biz['status'] === 'active');
                $rows[] = array_merge($biz, [
                    'user_id'     => $userIds[$i % count($userIds)],
                    'is_approved' => $isApproved,
                    'created_at'  => $createdAt,
                    'updated_at'  => $createdAt,
                ]);
            }

            DB::table('businesses')->insert($rows);
        }
    }

    private function seedDriverProfiles(): void
    {
        if (DB::table('driver_profiles')->count() === 0) {
            $userIds = DB::table('users')->pluck('id')->toArray();
            if (count($userIds) < 4) return;
            $drivers = [
                [
                    'user_id'        => $userIds[0],
                    'vehicle_model'  => 'Toyota Camry 2023',
                    'vehicle_plate'  => '8ABC123',
                    'license_number' => 'DL98765432',
                    'status'         => 'active',
                    'created_at'     => now()->subDays(100),
                    'updated_at'     => now(),
                ],
                [
                    'user_id'        => $userIds[1],
                    'vehicle_model'  => 'Honda Civic 2024',
                    'vehicle_plate'  => '9DEF456',
                    'license_number' => 'DL87654321',
                    'status'         => 'active',
                    'created_at'     => now()->subDays(80),
                    'updated_at'     => now(),
                ],
                [
                    'user_id'        => $userIds[2],
                    'vehicle_model'  => 'Hyundai Sonata 2025',
                    'vehicle_plate'  => '7GHI789',
                    'license_number' => 'DL76543210',
                    'status'         => 'pending',
                    'created_at'     => now()->subDays(1),
                    'updated_at'     => now(),
                ],
                [
                    'user_id'        => $userIds[3],
                    'vehicle_model'  => 'Kia EV6 2024',
                    'vehicle_plate'  => '6JKL012',
                    'license_number' => 'DL65432109',
                    'status'         => 'pending',
                    'created_at'     => now(),
                    'updated_at'     => now(),
                ],
            ];
            DB::table('driver_profiles')->insert($drivers);
        }
    }

    private function seedElderSettings(): void
    {
        if (DB::table('elder_settings')->count() === 0) {
            $userIds = $this->getUserIds();
            if (count($userIds) < 5) return;

            $now = Carbon::now();

            // Pick 5 distinct users for elder settings
            $elderUserIds = array_slice($userIds, 0, 5);

            $guardians = [
                ['name' => '김영수', 'phone' => '213-555-1001'],
                ['name' => '이미영', 'phone' => '714-555-2002'],
                ['name' => '박준호', 'phone' => '310-555-3003'],
                ['name' => '최서연', 'phone' => '213-555-4004'],
                ['name' => '한지영', 'phone' => '949-555-5005'],
            ];

            $rows = [];
            foreach ($elderUserIds as $i => $userId) {
                $lastCheckin = $now->copy()->subHours(rand(1, 48));
                $isOverdue = $lastCheckin->diffInHours($now) > 24;

                $rows[] = [
                    'user_id'          => $userId,
                    'elder_mode'       => true,
                    'guardian_name'    => $guardians[$i]['name'],
                    'guardian_phone'   => $guardians[$i]['phone'],
                    'guardian_email'   => strtolower(str_replace(' ', '', $guardians[$i]['name'])) . '@gmail.com',
                    'checkin_interval' => $i < 3 ? 24 : 12,
                    'last_checkin_at'  => $lastCheckin,
                    'last_sos_at'      => $i === 2 ? $now->copy()->subDays(5) : null,
                    'is_overdue'       => $isOverdue,
                    'alert_sent'       => $isOverdue && $i % 2 === 0,
                    'emergency_contact'=> $guardians[$i]['phone'],
                    'notes'            => $i === 0 ? '혼자 거주, 주 1회 방문 필요' : ($i === 3 ? '당뇨 관리 중' : null),
                    'created_at'       => $now->copy()->subDays(rand(30, 120)),
                    'updated_at'       => $lastCheckin,
                ];
            }

            DB::table('elder_settings')->insert($rows);
        }
    }
}
