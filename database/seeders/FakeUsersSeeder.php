<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Carbon\Carbon;

class FakeUsersSeeder extends Seeder
{
    public function run(): void
    {
        $password = Hash::make('password123');
        $now = Carbon::now();

        // ── 한국 성 30개 ──
        $lastNames = ['김','이','박','최','정','조','강','윤','임','한','오','신','서','권','황','안','송','유','홍','전','백','남','류','하','차','주','우','구','민','노'];

        // ── 한국 이름 30개 ──
        $firstNames = ['민준','서연','도현','지우','시우','하은','예준','수아','주원','지아','현우','서윤','준서','하린','지호','은서','건우','유나','승현','예린','태영','소율','원준','서현','재민','다은','성현','지민','윤호','채원'];

        // ── 영문 성 매핑 ──
        $lastNameEn = [
            '김'=>'kim','이'=>'lee','박'=>'park','최'=>'choi','정'=>'jung','조'=>'cho',
            '강'=>'kang','윤'=>'yoon','임'=>'lim','한'=>'han','오'=>'oh','신'=>'shin',
            '서'=>'seo','권'=>'kwon','황'=>'hwang','안'=>'ahn','송'=>'song','유'=>'yoo',
            '홍'=>'hong','전'=>'jeon','백'=>'baek','남'=>'nam','류'=>'ryu','하'=>'ha',
            '차'=>'cha','주'=>'joo','우'=>'woo','구'=>'koo','민'=>'min','노'=>'noh',
        ];

        // ── 영문 이름 매핑 ──
        $firstNameEn = [
            '민준'=>'minjun','서연'=>'seoyeon','도현'=>'dohyun','지우'=>'jiwoo','시우'=>'siwoo',
            '하은'=>'haeun','예준'=>'yejun','수아'=>'sua','주원'=>'juwon','지아'=>'jia',
            '현우'=>'hyunwoo','서윤'=>'seoyun','준서'=>'junseo','하린'=>'harin','지호'=>'jiho',
            '은서'=>'eunseo','건우'=>'gunwoo','유나'=>'yuna','승현'=>'seunghyun','예린'=>'yerin',
            '태영'=>'taeyoung','소율'=>'soyul','원준'=>'wonjun','서현'=>'seohyun','재민'=>'jaemin',
            '다은'=>'daeun','성현'=>'sunghyun','지민'=>'jimin','윤호'=>'yunho','채원'=>'chaewon',
        ];

        // ── 영문 이름 대체 (일부 유저는 미국식 이름 사용) ──
        $americanNames = [
            'david','jennifer','michael','sarah','james','jessica','daniel','grace',
            'chris','linda','andrew','emily','brian','michelle','kevin','alice',
            'eric','sophia','jason','olivia','peter','emma','ryan','hannah',
            'steve','ashley','john','amy','tony','chloe','paul','rachel',
            'sean','diana','mark','irene','dennis','tina','eddie','helen',
            'tommy','christine','jay','jane','eugene','stella','albert','crystal',
        ];

        // ── 자기소개 템플릿 ──
        $bioTemplates = [
            'LA' => [
                'LA 거주 %d년차 직장인입니다','코리아타운에서 식당 운영중','LA에서 IT 일하고 있어요',
                'LA 한인타운 토박이','남가주 거주, 운동 좋아해요','LA에서 부동산 공부중',
                'LA 직장인, 맛집 탐방 취미','서부 거주 10년차 워킹맘','LA에서 디자인 일해요',
                'LA 거주, 여행과 카페 좋아합니다','코리아타운 주민이에요','LA에서 회계사로 일합니다',
                'LA 살면서 한인 커뮤니티 활동중','남가주 IT 개발자입니다','LA 생활 즐기는 중',
            ],
            'NYC' => [
                '뉴욕 대학생, 맛집 탐방 좋아해요','맨해튼 직장인입니다','플러싱 거주 한인입니다',
                'NYC에서 금융업 종사중','뉴욕 생활 5년차','퀸즈 거주, 요리가 취미에요',
                '뉴욕에서 패션 일해요','맨해튼에서 마케팅 합니다','뉴욕 한인, 사진 찍기 좋아해요',
                'NYC 거주 프리랜서입니다',
            ],
            'Chicago' => [
                '시카고 거주 엔지니어','시카고에서 자영업 중','시카고 한인 커뮤니티 활동중',
                '시카고 대학원생입니다','중서부 거주, 골프 좋아해요',
            ],
            'Dallas' => [
                '달라스 거주 IT 종사자','텍사스에서 사업하고 있어요','달라스 한인입니다',
                'DFW 지역 부동산 관심 많아요','달라스 거주 직장인',
            ],
            'Atlanta' => [
                '애틀란타 거주 의료인','조지아 한인 커뮤니티 활동중','애틀란타에서 무역업 종사',
                '애틀란타 한인입니다','남동부 거주 직장인',
            ],
            'Seattle' => [
                '시애틀 IT 개발자입니다','시애틀 거주, 커피 좋아해요','워싱턴주 거주 엔지니어',
                '시애틀에서 스타트업 일해요','시애틀 한인 직장인',
            ],
            'Honolulu' => [
                '하와이 거주 한인입니다','호놀룰루에서 관광업 종사','하와이 생활 즐기고 있어요',
                '호놀룰루 거주 직장인',
            ],
            'Philadelphia' => [
                '필라델피아 대학원생','필라델피아 거주 연구원','동부 거주 한인입니다',
            ],
            'LasVegas' => [
                '라스베가스 거주 자영업자','베가스에서 호텔 일해요','라스베가스 한인 커뮤니티 활동중',
            ],
            'DC' => [
                'DC 거주 공무원입니다','워싱턴DC에서 로비스트 활동중','DC 한인 직장인',
            ],
        ];

        // ── 지역별 설정 ──
        $regions = [
            'LA' => [
                'count' => 60,
                'zips' => ['90004','90005','90006','90010','90012','90019','90020'],
                'streets' => ['Western Ave','Vermont Ave','Wilshire Blvd','Olympic Blvd','8th St','6th St','Normandie Ave','Irolo St','Kingsley Dr','Harvard Blvd','Serrano Ave','Alexandria Ave','Mariposa Ave','Catalina St','Kenmore Ave'],
                'city' => 'Los Angeles', 'state' => 'CA',
                'coords' => [
                    '90004' => [34.0762, -118.3089], '90005' => [34.0590, -118.3105],
                    '90006' => [34.0480, -118.2920], '90010' => [34.0610, -118.3020],
                    '90012' => [34.0660, -118.2400], '90019' => [34.0480, -118.3380],
                    '90020' => [34.0660, -118.3090],
                ],
                'area_code' => '213', 'ip_prefix' => ['104.28','172.67'],
            ],
            'NYC' => [
                'count' => 40,
                'zips' => ['10001','10002','10016','10036','11354','11355','11373'],
                'streets' => ['Broadway','5th Ave','Madison Ave','Lexington Ave','Park Ave','Main St','Union St','Northern Blvd','Roosevelt Ave','Kissena Blvd','Parsons Blvd','Bowne St','37th Ave','College Point Blvd'],
                'city_map' => ['10001'=>'New York','10002'=>'New York','10016'=>'New York','10036'=>'New York','11354'=>'Flushing','11355'=>'Flushing','11373'=>'Elmhurst'],
                'state' => 'NY',
                'coords' => [
                    '10001' => [40.7506, -73.9971], '10002' => [40.7157, -73.9863],
                    '10016' => [40.7459, -73.9781], '10036' => [40.7590, -73.9890],
                    '11354' => [40.7690, -73.8271], '11355' => [40.7548, -73.8206],
                    '11373' => [40.7389, -73.8785],
                ],
                'area_code' => '212', 'ip_prefix' => ['208.78','23.234'],
            ],
            'Chicago' => [
                'count' => 20,
                'zips' => ['60601','60614','60625'],
                'streets' => ['Michigan Ave','Clark St','Lincoln Ave','Western Ave','Lawrence Ave','Kedzie Ave','Foster Ave','Damen Ave'],
                'city' => 'Chicago', 'state' => 'IL',
                'coords' => [
                    '60601' => [41.8862, -87.6186], '60614' => [41.9220, -87.6490],
                    '60625' => [41.9720, -87.7020],
                ],
                'area_code' => '312', 'ip_prefix' => ['66.102','74.125'],
            ],
            'Dallas' => [
                'count' => 15,
                'zips' => ['75001','75019','75034'],
                'streets' => ['Main St','Commerce St','Elm St','Belt Line Rd','Coit Rd','Preston Rd','Legacy Dr','Lebanon Rd'],
                'city_map' => ['75001'=>'Addison','75019'=>'Coppell','75034'=>'Frisco'],
                'state' => 'TX',
                'coords' => [
                    '75001' => [32.9612, -96.8292], '75019' => [32.9546, -96.9842],
                    '75034' => [33.1507, -96.8236],
                ],
                'area_code' => '214', 'ip_prefix' => ['70.32','98.137'],
            ],
            'Atlanta' => [
                'count' => 15,
                'zips' => ['30024','30043','30096'],
                'streets' => ['Peachtree Rd','Buford Hwy','Pleasant Hill Rd','Satellite Blvd','Peachtree Industrial Blvd','Steve Reynolds Blvd'],
                'city_map' => ['30024'=>'Suwanee','30043'=>'Lawrenceville','30096'=>'Duluth'],
                'state' => 'GA',
                'coords' => [
                    '30024' => [34.0515, -84.0713], '30043' => [33.9562, -84.0022],
                    '30096' => [33.9607, -84.1455],
                ],
                'area_code' => '678', 'ip_prefix' => ['50.56','162.242'],
            ],
            'Seattle' => [
                'count' => 15,
                'zips' => ['98101','98104','98122'],
                'streets' => ['Pike St','Pine St','Madison St','Union St','Cherry St','James St','Yesler Way','Broadway'],
                'city' => 'Seattle', 'state' => 'WA',
                'coords' => [
                    '98101' => [47.6110, -122.3370], '98104' => [47.6015, -122.3310],
                    '98122' => [47.6125, -122.3050],
                ],
                'area_code' => '206', 'ip_prefix' => ['52.12','34.210'],
            ],
            'Honolulu' => [
                'count' => 10,
                'zips' => ['96814','96815','96817'],
                'streets' => ['King St','Kapiolani Blvd','Kalakaua Ave','Keeaumoku St','Piikoi St','Beretania St'],
                'city' => 'Honolulu', 'state' => 'HI',
                'coords' => [
                    '96814' => [21.2968, -157.8470], '96815' => [21.2740, -157.8235],
                    '96817' => [21.3280, -157.8570],
                ],
                'area_code' => '808', 'ip_prefix' => ['69.12','76.73'],
            ],
            'Philadelphia' => [
                'count' => 10,
                'zips' => ['19103','19104'],
                'streets' => ['Market St','Chestnut St','Walnut St','Spruce St','Pine St','Broad St','Lancaster Ave'],
                'city' => 'Philadelphia', 'state' => 'PA',
                'coords' => [
                    '19103' => [39.9533, -75.1726], '19104' => [39.9573, -75.1989],
                ],
                'area_code' => '215', 'ip_prefix' => ['68.87','75.75'],
            ],
            'LasVegas' => [
                'count' => 10,
                'zips' => ['89101','89109'],
                'streets' => ['Las Vegas Blvd','Fremont St','Charleston Blvd','Sahara Ave','Spring Mountain Rd','Desert Inn Rd'],
                'city' => 'Las Vegas', 'state' => 'NV',
                'coords' => [
                    '89101' => [36.1716, -115.1445], '89109' => [36.1270, -115.1680],
                ],
                'area_code' => '702', 'ip_prefix' => ['64.62','209.107'],
            ],
            'DC' => [
                'count' => 5,
                'zips' => ['20001','20036'],
                'streets' => ['K St NW','Connecticut Ave NW','M St NW','Pennsylvania Ave NW','16th St NW','Vermont Ave NW'],
                'city' => 'Washington', 'state' => 'DC',
                'coords' => [
                    '20001' => [38.9100, -77.0180], '20036' => [38.9076, -77.0410],
                ],
                'area_code' => '202', 'ip_prefix' => ['38.99','68.100'],
            ],
        ];

        // ── 이메일 도메인 ──
        $emailDomains = ['gmail.com','gmail.com','gmail.com','yahoo.com','naver.com'];

        // ── 닉네임 구분자 ──
        $separators = ['_','.','_','','_'];

        // ── 200명 유저 생성 ──
        $users = [];
        $usedEmails = [];
        $usedUsernames = [];
        $userIndex = 0;

        foreach ($regions as $regionKey => $regionConfig) {
            for ($i = 0; $i < $regionConfig['count']; $i++) {
                $userIndex++;
                $lastName = $lastNames[array_rand($lastNames)];
                $firstName = $firstNames[array_rand($firstNames)];
                $fullName = $lastName . $firstName;

                // 50% 확률로 미국식 이름 사용 (닉네임용)
                $useAmericanName = rand(0, 1);
                $enFirst = $useAmericanName
                    ? $americanNames[array_rand($americanNames)]
                    : $firstNameEn[$firstName];
                $enLast = $lastNameEn[$lastName];

                // 닉네임 생성 (다양한 패턴)
                $sep = $separators[array_rand($separators)];
                $suffix = rand(0, 3) === 0 ? '' : (string)rand(1, 99);
                $pattern = rand(0, 4);
                switch ($pattern) {
                    case 0: $username = $enFirst . $sep . $enLast . $suffix; break;
                    case 1: $username = $enLast . $sep . $enFirst . $suffix; break;
                    case 2: $username = $enFirst . $suffix . $sep . $enLast; break;
                    case 3: $username = $enFirst . $enLast[0] . $suffix; break;
                    default: $username = $enFirst . $sep . $enLast . rand(10, 99); break;
                }
                $username = strtolower(preg_replace('/[^a-z0-9._]/', '', strtolower($username)));

                // 유니크 보장
                while (isset($usedUsernames[$username]) || strlen($username) < 4) {
                    $username .= rand(1, 99);
                }
                $usedUsernames[$username] = true;

                // 이메일
                $emailDomain = $emailDomains[array_rand($emailDomains)];
                $email = $username . '@' . $emailDomain;
                while (isset($usedEmails[$email])) {
                    $email = $username . rand(1, 999) . '@' . $emailDomain;
                }
                $usedEmails[$email] = true;

                // 주소
                $zip = $regionConfig['zips'][array_rand($regionConfig['zips'])];
                $street = $regionConfig['streets'][array_rand($regionConfig['streets'])];
                $streetNum = rand(100, 9999);
                $city = $regionConfig['city_map'][$zip] ?? $regionConfig['city'];
                $state = $regionConfig['state'];
                $address = "{$streetNum} {$street}";
                $fullAddress = "{$address}, {$city}, {$state} {$zip}";

                // 좌표 (약간 랜덤 오프셋)
                $baseCoords = $regionConfig['coords'][$zip];
                $lat = round($baseCoords[0] + (rand(-50, 50) / 10000), 4);
                $lng = round($baseCoords[1] + (rand(-50, 50) / 10000), 4);

                // 전화번호
                $areaCode = $regionConfig['area_code'];
                $phone = $areaCode . '-' . rand(200, 999) . '-' . str_pad(rand(0, 9999), 4, '0', STR_PAD_LEFT);

                // IP 주소
                $ipPrefix = $regionConfig['ip_prefix'][array_rand($regionConfig['ip_prefix'])];
                $ip = $ipPrefix . '.' . rand(1, 254) . '.' . rand(1, 254);

                // 포인트 & 레벨
                $points = rand(50, 8000);
                $level = match (true) {
                    $points >= 50000 => '참나무',
                    $points >= 20000 => '숲',
                    $points >= 5000  => '나무',
                    $points >= 1000  => '새싹',
                    default          => '씨앗',
                };

                // 자기소개
                $bios = $bioTemplates[$regionKey];
                $bio = $bios[array_rand($bios)];
                $bio = str_replace('%d', rand(3, 15), $bio);

                // 가입일 (최근 180일 이내)
                $createdAt = Carbon::now()->subDays(rand(1, 180))->subHours(rand(0, 23))->subMinutes(rand(0, 59));

                // region 값 (도시명)
                $regionLabel = $city . ', ' . $state;

                $users[] = [
                    'name'              => $fullName,
                    'username'          => $username,
                    'nickname'          => $username,
                    'email'             => $email,
                    'email_verified_at' => rand(0, 4) > 0 ? $createdAt->copy()->addHours(rand(1, 48)) : null,
                    'password'          => $password,
                    'phone'             => $phone,
                    'avatar'            => null,
                    'region'            => $regionLabel,
                    'address'           => $fullAddress,
                    'address2'          => rand(0, 3) === 0 ? 'Apt ' . rand(1, 999) : null,
                    'city'              => $city,
                    'state'             => $state,
                    'zip_code'          => $zip,
                    'lat'               => $lat,
                    'lng'               => $lng,
                    'level'             => $level,
                    'points_total'      => $points,
                    'cash_balance'      => 0,
                    'is_elder'          => false,
                    'is_driver'         => false,
                    'lang'              => 'ko',
                    'status'            => 'active',
                    'is_admin'          => false,
                    'last_login_at'     => Carbon::now()->subDays(rand(0, 30))->subHours(rand(0, 23)),
                    'bio'               => $bio,
                    'kakao_id'          => null,
                    'telegram_id'       => null,
                    'created_at'        => $createdAt,
                    'updated_at'        => $createdAt,
                ];
            }
        }

        // ── 50명씩 chunk 삽입 ──
        $chunks = array_chunk($users, 50);
        foreach ($chunks as $chunk) {
            DB::table('users')->insert($chunk);
        }

        $this->command->info("✓ 가상 유저 " . count($users) . "명 생성 완료");

        // ── user_wallets 생성 ──
        $this->seedWallets();
    }

    private function seedWallets(): void
    {
        // 방금 생성한 유저들 (is_admin=false, 최근 180일 이내 가입)
        $fakeUsers = DB::table('users')
            ->where('is_admin', false)
            ->where('created_at', '>=', Carbon::now()->subDays(181))
            ->orderBy('id')
            ->get(['id', 'points_total']);

        $wallets = [];
        $transactions = [];
        $now = Carbon::now();

        foreach ($fakeUsers as $user) {
            $coinBalance = rand(500, 5000);
            $lifetimeEarned = $coinBalance * rand(2, 5);

            $wallets[] = [
                'user_id'          => $user->id,
                'star_balance'     => rand(0, 200),
                'gem_balance'      => rand(0, 50),
                'coin_balance'     => $coinBalance,
                'chip_balance'     => rand(0, 500),
                'lifetime_earned'  => $lifetimeEarned,
                'created_at'       => $now,
                'updated_at'       => $now,
            ];

            $transactions[] = [
                'user_id'       => $user->id,
                'type'          => 'signup',
                'currency'      => 'coin',
                'amount'        => 1000,
                'balance_after' => $coinBalance,
                'description'   => '가입 보너스',
                'created_at'    => $now,
                'updated_at'    => $now,
            ];
        }

        // 50명씩 chunk 삽입
        foreach (array_chunk($wallets, 50) as $chunk) {
            DB::table('user_wallets')->insert($chunk);
        }
        foreach (array_chunk($transactions, 50) as $chunk) {
            DB::table('wallet_transactions')->insert($chunk);
        }

        $this->command->info("✓ 지갑 " . count($wallets) . "개 생성 완료");
    }
}
