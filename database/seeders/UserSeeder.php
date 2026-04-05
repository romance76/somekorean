<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class UserSeeder extends Seeder
{
    public function run(): void
    {
        // ── Admin ───────────────────────────────────────────────
        User::create([
            'name'       => '관리자',
            'nickname'   => 'Admin',
            'email'      => 'admin@somekorean.com',
            'password'   => Hash::make('password'),
            'role'       => 'admin',
            'phone'      => '2135551000',
            'language'   => 'ko',
            'points'     => 99999,
            'game_points'=> 99999,
            'city'       => 'Los Angeles',
            'state'      => 'CA',
            'zipcode'    => '90010',
            'latitude'   => 34.0622,
            'longitude'  => -118.3095,
            'address'    => '3250 Wilshire Blvd',
            'bio'        => 'SomeKorean 관리자입니다.',
            'email_verified_at' => now(),
            'last_login_at' => now(),
            'login_count' => 100,
        ]);

        // ── Name pools ──────────────────────────────────────────
        $lastNames = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전'];
        $firstNames = ['민수', '지영', '현우', '서연', '준호', '하나', '성민', '유진', '태현', '수빈', '영호', '미영', '정훈', '소연', '동현', '은지', '상현', '지은', '병철', '혜진'];
        $engFirstNames = ['James', 'Sarah', 'David', 'Jenny', 'Michael', 'Grace', 'Daniel', 'Michelle', 'Chris', 'Ashley', 'Brian', 'Cathy', 'Paul', 'Diane', 'Steve', 'Elaine', 'Kevin', 'Fiona', 'Henry', 'Iris'];
        $engLastNames = ['Kim', 'Lee', 'Park', 'Choi', 'Jung', 'Kang', 'Cho', 'Yoon', 'Jang', 'Lim', 'Han', 'Oh', 'Seo', 'Shin', 'Kwon', 'Hwang', 'Ahn', 'Song', 'Ryu', 'Jun'];

        // ── City data ───────────────────────────────────────────
        $cities = [
            ['city' => 'Los Angeles',    'state' => 'CA', 'lat' => 34.0522, 'lng' => -118.2437, 'zips' => ['90004','90005','90006','90010','90019','90020','90036','90038','90057','90071'], 'addresses' => ['3250 Wilshire Blvd','450 S Western Ave','621 S Virgil Ave','3550 W 6th St','2936 W 8th St','4121 W 3rd St','880 S La Brea Ave','5959 Hollywood Blvd','2700 W Olympic Blvd','333 S Grand Ave']],
            ['city' => 'New York',       'state' => 'NY', 'lat' => 40.7128, 'lng' => -74.0060,  'zips' => ['10001','10002','10003','10011','10013','10016','10019','10022','10036','11354'], 'addresses' => ['149-06 41st Ave','136-80 39th Ave','41-01 Kissena Blvd','32-06 Union St','35-19 Broadway','45-37 Bowne St','144-11 Northern Blvd','71-28 Roosevelt Ave','40-09 Prince St','36-09 Main St']],
            ['city' => 'Chicago',        'state' => 'IL', 'lat' => 41.8781, 'lng' => -87.6298,  'zips' => ['60601','60605','60607','60611','60614','60618','60625','60640','60647','60657'], 'addresses' => ['3516 W Lawrence Ave','5014 N Lincoln Ave','4823 N Broadway','2659 W Lawrence Ave','3257 W Bryn Mawr Ave','2717 W Peterson Ave','5400 N Clark St','4010 N Kedzie Ave','3455 N Sheffield Ave','2845 W Diversey Ave']],
            ['city' => 'Atlanta',        'state' => 'GA', 'lat' => 33.7490, 'lng' => -84.3880,  'zips' => ['30305','30306','30308','30309','30318','30324','30326','30338','30339','30341'], 'addresses' => ['5150 Buford Hwy','3255 Chamblee Dunwoody Rd','2345 Cheshire Bridge Rd','3050 Peachtree Rd NW','6035 Peachtree Rd','4897 Buford Hwy','2625 Piedmont Rd','4300 Buford Hwy','3535 Peachtree Rd NE','5495 Jimmy Carter Blvd']],
            ['city' => 'Dallas',         'state' => 'TX', 'lat' => 32.7767, 'lng' => -96.7970,  'zips' => ['75006','75024','75034','75040','75056','75062','75075','75081','75201','75219'], 'addresses' => ['2625 Old Denton Rd','8236 Spring Valley Rd','2540 Royal Ln','11110 Dennis Rd','400 N Greenville Ave','3535 Belt Line Rd','1505 E Beltline Rd','2540 Old Denton Rd','330 E Abram St','3920 W Northwest Hwy']],
            ['city' => 'Houston',        'state' => 'TX', 'lat' => 29.7604, 'lng' => -95.3698,  'zips' => ['77036','77040','77042','77056','77057','77072','77077','77082','77083','77084'], 'addresses' => ['9896 Bellaire Blvd','1005 Blalock Rd','2400 Fountain View Dr','9888 Bellaire Blvd','6128 Wilcrest Dr','1003 Dairy Ashford','12345 Westheimer Rd','9780 SW Fwy','11811 Wilcrest Dr','2520 Dulles Ave']],
            ['city' => 'Seattle',        'state' => 'WA', 'lat' => 47.6062, 'lng' => -122.3321, 'zips' => ['98101','98104','98109','98112','98115','98122','98133','98144','98155','98188'], 'addresses' => ['515 Broadway E','602 S King St','312 2nd Ave S','1963 S Lander St','611 S Lane St','800 S Jackson St','1401 NW 56th St','6315 Roosevelt Way NE','303 Battery St','15030 Aurora Ave N']],
            ['city' => 'San Francisco',  'state' => 'CA', 'lat' => 37.7749, 'lng' => -122.4194, 'zips' => ['94102','94103','94107','94108','94109','94112','94115','94116','94118','94122'], 'addresses' => ['4301 Geary Blvd','501 Balboa St','2345 Clement St','615 Jackson St','737 Post St','818 Irving St','3300 Geary Blvd','1550 Howard St','2111 Clement St','5550 Geary Blvd']],
            ['city' => 'Washington',     'state' => 'DC', 'lat' => 38.9072, 'lng' => -77.0369,  'zips' => ['20001','20002','20003','20005','20007','20009','20036','20037','22003','22042'], 'addresses' => ['2915 Columbia Pike','6228 Little River Tpke','4231 Markham St','7350 Heritage Village Plz','3217 N Pershing Dr','2701 Wilson Blvd','1529 14th St NW','809 H St NW','1112 16th St NW','1789 Lanier Pl NW']],
            ['city' => 'Philadelphia',   'state' => 'PA', 'lat' => 39.9526, 'lng' => -75.1652,  'zips' => ['19102','19103','19104','19106','19107','19120','19124','19130','19140','19148'], 'addresses' => ['939 Race St','225 N 10th St','207 N Juniper St','130 N 10th St','110 N 9th St','324 Arch St','930 Race St','608 S 9th St','1013 Race St','200 N 10th St']],
        ];

        $bios = [
            'LA 거주 10년차입니다. 한인타운에서 일하고 있어요.',
            '뉴욕에서 직장생활 중입니다. 플러싱에 살아요.',
            '시카고 북부에 거주하고 있습니다. 주말에는 골프를 즐깁니다.',
            '아틀란타에서 작은 가게를 운영하고 있어요.',
            '달라스로 이사온 지 3년 됐습니다.',
            '휴스턴에서 가족과 함께 살고 있습니다.',
            '시애틀 IT 회사에서 근무 중입니다.',
            '샌프란시스코에서 유학 중인 학생입니다.',
            'DC 근처에서 연방 정부 일을 하고 있어요.',
            '필라델피아 한인회에서 봉사활동을 하고 있습니다.',
            '맛집 탐방을 좋아하는 직장인입니다.',
            '두 아이의 엄마예요. 육아 정보 공유해요!',
            '부동산 에이전트로 일하고 있습니다.',
            '요리를 좋아하는 회사원입니다. 레시피 많이 올릴게요.',
            '이민 20년차입니다. 궁금한 거 물어보세요.',
            '대학원에서 공부하고 있는 유학생입니다.',
            '운동을 좋아합니다. 같이 운동할 분 찾아요!',
            '음악 듣는 게 취미인 직장인입니다.',
            '사진 촬영이 취미입니다. 좋은 사진 공유할게요.',
            '한국 드라마, K-POP 좋아합니다!',
        ];

        $rows = [];
        $now  = now();
        $password = Hash::make('password');

        for ($i = 0; $i < 200; $i++) {
            $city = $cities[array_rand($cities)];

            // 60% Korean name, 40% English name
            if (rand(1, 100) <= 60) {
                $name     = $lastNames[array_rand($lastNames)] . $firstNames[array_rand($firstNames)];
                $nickname = $name;
            } else {
                $engFirst = $engFirstNames[array_rand($engFirstNames)];
                $engLast  = $engLastNames[array_rand($engLastNames)];
                $name     = $engFirst . ' ' . $engLast;
                $nickname = $engFirst;
            }

            // Slight lat/lng jitter within city
            $lat = $city['lat'] + (rand(-300, 300) / 10000);
            $lng = $city['lng'] + (rand(-300, 300) / 10000);

            $rows[] = [
                'name'              => $name,
                'nickname'          => $nickname,
                'email'             => 'user' . ($i + 1) . '@somekorean.com',
                'email_verified_at' => rand(0, 100) > 10 ? $now : null,
                'password'          => $password,
                'phone'             => (string) rand(2010000000, 9999999999),
                'address'           => $city['addresses'][array_rand($city['addresses'])],
                'city'              => $city['city'],
                'state'             => $city['state'],
                'zipcode'           => $city['zips'][array_rand($city['zips'])],
                'latitude'          => round($lat, 7),
                'longitude'         => round($lng, 7),
                'avatar'            => null,
                'bio'               => $bios[array_rand($bios)],
                'language'          => rand(1, 100) <= 80 ? 'ko' : 'en',
                'points'            => rand(0, 5000),
                'game_points'       => rand(0, 3000),
                'role'              => 'user',
                'is_banned'         => false,
                'last_login_at'     => $now->copy()->subDays(rand(0, 30)),
                'login_count'       => rand(1, 200),
                'created_at'        => $now->copy()->subDays(rand(0, 90)),
                'updated_at'        => $now,
            ];
        }

        // Insert in chunks for performance
        foreach (array_chunk($rows, 50) as $chunk) {
            User::insert($chunk);
        }

        $this->command->info('UserSeeder: 1 admin + 200 users created');
    }
}
