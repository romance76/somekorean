<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class Phase5DataSeeder extends Seeder
{
    public function run(): void
    {
        $allUids = DB::table('users')->pluck('id')->toArray();
        if (empty($allUids)) {
            $this->command->error('No users found. Run DemoDataSeeder first.');
            return;
        }

        // ── 동호회 (Clubs) ──────────────────────────────────────
        if (DB::table('clubs')->count() === 0) {
            $clubData = [
                ['name'=>'LA 한인 축구클럽',        'category'=>'스포츠',    'region'=>'Los Angeles',   'desc'=>'매주 토요일 LA에서 즐기는 한인 축구 모임입니다. 초급부터 중급까지 누구나 환영!',    'count'=>34],
                ['name'=>'뉴욕 요리 동호회',         'category'=>'음식/요리', 'region'=>'New York',      'desc'=>'한국 가정식부터 퓨전 요리까지, 함께 요리하고 나눠먹는 즐거운 모임입니다.',          'count'=>28],
                ['name'=>'시카고 독서 모임',         'category'=>'취미/여가', 'region'=>'Chicago',       'desc'=>'한국어 원서와 영어 원서를 함께 읽고 토론하는 독서 모임. 월 2회 미팅.',             'count'=>19],
                ['name'=>'SF 한인 등산 클럽',        'category'=>'스포츠',    'region'=>'San Francisco', 'desc'=>'베이에어리어 근교 산행을 함께합니다. 매월 첫째 일요일 출발!',                      'count'=>45],
                ['name'=>'달라스 엄마들 육아모임',   'category'=>'육아/교육', 'region'=>'Dallas',        'desc'=>'미국에서 아이 키우는 한인 엄마들의 정보공유 및 친목 모임입니다.',                   'count'=>52],
                ['name'=>'애틀랜타 비즈니스 네트워크','category'=>'비즈니스', 'region'=>'Atlanta',       'desc'=>'한인 사업가들의 네트워킹 & 정보교류 모임. 월 1회 런치 미팅.',                      'count'=>23],
                ['name'=>'시애틀 테니스 클럽',       'category'=>'스포츠',    'region'=>'Seattle',       'desc'=>'매주 수요일 저녁 테니스 즐겨요! 실력 무관 누구나 환영합니다.',                     'count'=>17],
                ['name'=>'휴스턴 한인 사진 동호회',  'category'=>'취미/여가', 'region'=>'Houston',       'desc'=>'사진 찍기를 좋아하는 한인들의 모임. 출사와 전시 활동을 함께해요.',                  'count'=>31],
                ['name'=>'보스턴 한인 교회 청년부',  'category'=>'종교',      'region'=>'Boston',        'desc'=>'보스턴 한인 청년들의 신앙 공동체. 주일 예배 후 교제.',                             'count'=>40],
                ['name'=>'마이애미 서핑 클럽',       'category'=>'스포츠',    'region'=>'Miami',         'desc'=>'마이애미 해변에서 서핑 배우고 즐기는 한인 서퍼들의 모임!',                         'count'=>22],
            ];
            foreach ($clubData as $club) {
                $creatorId = $allUids[array_rand($allUids)];
                $clubId = DB::table('clubs')->insertGetId([
                    'creator_id'   => $creatorId,
                    'name'         => $club['name'],
                    'category'     => $club['category'],
                    'description'  => $club['desc'],
                    'region'       => $club['region'],
                    'member_count' => $club['count'],
                    'is_approval'  => false,
                    'created_at'   => Carbon::now()->subDays(rand(10, 180)),
                    'updated_at'   => Carbon::now(),
                ]);
                DB::table('club_members')->insert([
                    'club_id' => $clubId, 'user_id' => $creatorId,
                    'role' => 'owner', 'status' => 'approved',
                    'created_at' => Carbon::now()->subDays(5), 'updated_at' => Carbon::now(),
                ]);
                $members = array_slice($allUids, 0, rand(3, 8));
                foreach ($members as $uid) {
                    if ($uid === $creatorId) continue;
                    try {
                        DB::table('club_members')->insert([
                            'club_id' => $clubId, 'user_id' => $uid,
                            'role' => 'member', 'status' => 'approved',
                            'created_at' => Carbon::now()->subDays(rand(1, 30)), 'updated_at' => Carbon::now(),
                        ]);
                    } catch (\Exception $e) {}
                }
            }
            $this->command->info('Clubs seeded: 10');
        } else {
            $this->command->info('Clubs already exist, skipping.');
        }

        // ── 공동구매 (Group Buys) ───────────────────────────────
        if (DB::table('group_buys')->count() === 0) {
            $gbData = [
                ['title'=>'오가닉 들기름 공동구매',         'cat'=>'food',      'price'=>45.00,  'min'=>5,  'desc'=>'국내산 들깨 100% 오가닉 들기름. 최소 5명 모이면 30% 할인!'],
                ['title'=>'한국 떡볶이 소스 박스세트',      'cat'=>'food',      'price'=>35.00,  'min'=>10, 'desc'=>'정통 떡볶이 소스 + 어묵 세트. 배송비 절약 공동구매'],
                ['title'=>'에어프라이어 5.8QT 공구',        'cat'=>'appliance', 'price'=>89.99,  'min'=>8,  'desc'=>'아마존 베스트셀러 에어프라이어 공동구매. 정가대비 25% 절약'],
                ['title'=>'한국산 홍삼정 공동구매',         'cat'=>'health',    'price'=>120.00, 'min'=>5,  'desc'=>'정관장 홍삼정 30포. 면세점 가격보다 저렴하게 구매'],
                ['title'=>'유아 수영복 여름 공구',          'cat'=>'kids',      'price'=>28.00,  'min'=>15, 'desc'=>'국내 유명 브랜드 유아 수영복 사이즈 다양. 15명부터 40% 할인'],
                ['title'=>'냉동 삼겹살 5파운드 공구',       'cat'=>'food',      'price'=>55.00,  'min'=>6,  'desc'=>'한국산 냉동 삼겹살 5lb. LA한인마트보다 20% 저렴하게!'],
                ['title'=>'샤오미 로봇청소기 X10 공동구매', 'cat'=>'appliance', 'price'=>399.00, 'min'=>4,  'desc'=>'샤오미 최신 로봇청소기 공동구매. 정가 $499 → 공구가 $399'],
                ['title'=>'한국어 교재 세트 공구 유아용',   'cat'=>'education', 'price'=>85.00,  'min'=>8,  'desc'=>'미국에서 한국어 교육을 위한 교재 세트. 언어발달 전문가 추천'],
                ['title'=>'코스트코 한국식품 공동구매',     'cat'=>'food',      'price'=>95.00,  'min'=>5,  'desc'=>'코스트코 한국 식품 모음 (신라면, 미역, 참기름 등) 대량구매'],
                ['title'=>'여름 선크림 한국 브랜드 공구',   'cat'=>'beauty',    'price'=>32.00,  'min'=>12, 'desc'=>'아누아/라운드랩 썬크림 공동구매. 12명 모이면 바로 발송'],
            ];
            $userIds = array_slice($allUids, 0, 10);
            foreach ($gbData as $i => $gb) {
                DB::table('group_buys')->insert([
                    'user_id'          => $userIds[$i % count($userIds)],
                    'title'            => $gb['title'],
                    'description'      => $gb['desc'],
                    'target_price'     => $gb['price'],
                    'min_participants' => $gb['min'],
                    'max_participants' => $gb['min'] * 5,
                    'category'         => $gb['cat'],
                    'status'           => 'open',
                    'deadline'         => Carbon::now()->addDays(rand(7, 30)),
                    'created_at'       => Carbon::now()->subDays(rand(1, 14)),
                    'updated_at'       => Carbon::now(),
                ]);
            }
            $this->command->info('Group buys seeded: 10');
        } else {
            $this->command->info('Group buys already exist, skipping.');
        }

        // ── 멘토 (Mentors) ────────────────────────────────────
        if (DB::table('mentors')->count() === 0) {
            $mentorData = [
                ['field'=>'IT/소프트웨어', 'years'=>8,  'company'=>'Google',     'position'=>'Senior Software Engineer', 'skills'=>['Python','Java','Cloud'],     'bio'=>'구글 시니어 엔지니어. 개발자 취업, 이직, 미국 IT업계 적응 멘토링 가능합니다.'],
                ['field'=>'의료/헬스케어', 'years'=>12, 'company'=>'Kaiser',     'position'=>'Physician',                'skills'=>['의대입시','레지던트','의사면허'],'bio'=>'미국 내과 전문의. 의대 입시부터 전문의까지 의료계 진로 전반 조언 드립니다.'],
                ['field'=>'비즈니스/경영', 'years'=>10, 'company'=>'McKinsey',   'position'=>'Senior Manager',           'skills'=>['MBA','컨설팅','전략기획'],   'bio'=>'맥킨지 시니어 매니저. MBA 진학, 컨설팅 커리어, 스타트업 창업 멘토링.'],
                ['field'=>'법률/이민',     'years'=>15, 'company'=>'Kim & Park', 'position'=>'Attorney',                 'skills'=>['이민법','취업비자','영주권'],'bio'=>'이민 전문 변호사. 비자 종류별 조언, 영주권 신청, 시민권 준비 도와드립니다.'],
                ['field'=>'금융/투자',     'years'=>7,  'company'=>'JPMorgan',   'position'=>'Financial Advisor',        'skills'=>['주식투자','부동산','세금'],  'bio'=>'JP모건 금융 어드바이저. 미국 주식, 부동산 투자, 세금 절감 전략 안내.'],
                ['field'=>'교육/입시',     'years'=>9,  'company'=>'Harvard Edu','position'=>'Education Consultant',     'skills'=>['대입준비','SAT','장학금'],   'bio'=>'하버드 출신 교육 컨설턴트. 미국 대학 입시 전략, 장학금 신청 멘토링.'],
                ['field'=>'마케팅/광고',   'years'=>6,  'company'=>'Meta',       'position'=>'Marketing Manager',        'skills'=>['디지털마케팅','SNS','광고'], 'bio'=>'메타 마케팅 매니저. 디지털 마케팅, SNS 전략, 한인 브랜드 미국 진출 조언.'],
                ['field'=>'창업/스타트업', 'years'=>5,  'company'=>'Techstars',  'position'=>'Startup Founder',          'skills'=>['창업','투자유치','피칭'],    'bio'=>'시리즈A 스타트업 대표. 창업 아이디어 검증, 투자 유치, 피칭 덱 작성 도움.'],
                ['field'=>'부동산',        'years'=>11, 'company'=>'Realty One', 'position'=>'Real Estate Broker',       'skills'=>['주택구매','투자','모기지'],  'bio'=>'LA 부동산 브로커. 첫 집 구매, 투자용 부동산, 모기지 전략 상담.'],
                ['field'=>'IT/소프트웨어', 'years'=>4,  'company'=>'Amazon',     'position'=>'Data Scientist',           'skills'=>['ML','데이터분석','취업'],    'bio'=>'아마존 데이터 사이언티스트. ML 포트폴리오, 데이터 직군 취업 멘토링.'],
            ];
            $mentorUserIds = array_slice($allUids, 10, 10);
            foreach ($mentorData as $i => $m) {
                // Skip if user already has a mentor profile
                $uid = $mentorUserIds[$i % count($mentorUserIds)];
                if (DB::table('mentors')->where('user_id', $uid)->exists()) continue;
                DB::table('mentors')->insert([
                    'user_id'          => $uid,
                    'field'            => $m['field'],
                    'bio'              => $m['bio'],
                    'years_experience' => $m['years'],
                    'company'          => $m['company'],
                    'position'         => $m['position'],
                    'skills'           => json_encode($m['skills'], JSON_UNESCAPED_UNICODE),
                    'is_available'     => true,
                    'created_at'       => Carbon::now()->subDays(rand(1, 60)),
                    'updated_at'       => Carbon::now(),
                ]);
            }
            $this->command->info('Mentors seeded: 10');
        } else {
            $this->command->info('Mentors already exist, skipping.');
        }

        // ── 라이드 (Rides) ────────────────────────────────────
        if (DB::table('rides')->count() === 0) {
            $rideData = [
                ['from'=>'Koreatown, Los Angeles',   'to'=>'LAX Airport',            'fare'=>35.00, 'dist'=>12.5],
                ['from'=>'Flushing, Queens NY',      'to'=>'JFK Airport',            'fare'=>42.00, 'dist'=>15.2],
                ['from'=>'Annandale, Virginia',      'to'=>'Dulles Airport',         'fare'=>55.00, 'dist'=>22.0],
                ['from'=>'Koreatown, Los Angeles',   'to'=>'Santa Monica',           'fare'=>28.00, 'dist'=>10.8],
                ['from'=>'Buford Highway, Atlanta',  'to'=>'ATL Airport',            'fare'=>38.00, 'dist'=>14.3],
                ['from'=>'Palisades Park, NJ',       'to'=>'Manhattan Koreatown',    'fare'=>25.00, 'dist'=>8.5],
                ['from'=>'Irvine, CA',               'to'=>'Koreatown, Los Angeles', 'fare'=>48.00, 'dist'=>18.0],
                ['from'=>'Lynnwood, WA',             'to'=>'Seattle Downtown',       'fare'=>32.00, 'dist'=>12.0],
                ['from'=>'Sugar Land, TX',           'to'=>'Houston Koreatown',      'fare'=>22.00, 'dist'=>8.0],
                ['from'=>"Naperville, IL",           'to'=>"Chicago O'Hare Airport", 'fare'=>45.00, 'dist'=>16.5],
            ];
            $passengerIds = array_slice($allUids, 0, 10);
            $driverIds    = array_slice($allUids, 20, 10);
            $methods = ['cash', 'card', 'points'];
            foreach ($rideData as $i => $rd) {
                $completedAt = Carbon::now()->subHours(rand(1, 720));
                DB::table('rides')->insert([
                    'passenger_id'     => $passengerIds[$i % count($passengerIds)],
                    'driver_id'        => $driverIds[$i % count($driverIds)],
                    'status'           => 'completed',
                    'pickup_address'   => $rd['from'],
                    'dropoff_address'  => $rd['to'],
                    'estimated_fare'   => $rd['fare'],
                    'final_fare'       => $rd['fare'],
                    'platform_fee'     => round($rd['fare'] * 0.15, 2),
                    'payment_method'   => $methods[array_rand($methods)],
                    'rating_driver'    => rand(4, 5),
                    'rating_passenger' => rand(4, 5),
                    'distance_miles'   => $rd['dist'],
                    'requested_at'     => $completedAt->copy()->subMinutes(rand(10, 30)),
                    'matched_at'       => $completedAt->copy()->subMinutes(rand(5, 10)),
                    'started_at'       => $completedAt->copy()->subMinutes(rand(2, 5)),
                    'completed_at'     => $completedAt,
                    'created_at'       => $completedAt->copy()->subMinutes(30),
                    'updated_at'       => $completedAt,
                ]);
            }
            $this->command->info('Rides seeded: 10');
        } else {
            $this->command->info('Rides already exist, skipping.');
        }

        $this->command->info('Phase5DataSeeder completed!');
    }
}
