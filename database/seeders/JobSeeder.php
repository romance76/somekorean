<?php

namespace Database\Seeders;

use App\Models\JobPost;
use App\Models\User;
use Illuminate\Database\Seeder;

class JobSeeder extends Seeder
{
    public function run(): void
    {
        $userIds = User::pluck('id')->toArray();
        if (empty($userIds)) {
            $this->command->warn('JobSeeder: no users found, skipping.');
            return;
        }

        $categoryJobs = [
            'restaurant' => [
                'titles'       => ['한식당 주방 보조 구합니다', '서버/웨이트리스 모집', '스시 셰프 구인', '카페 바리스타 채용', '한인 식당 홀 매니저 구합니다', '제과점 베이커 모집', '배달 드라이버 구합니다', '프랜차이즈 매장 매니저 구인'],
                'companies'    => ['서울 한식당', '대박 BBQ', '동경 스시', '카페 봄', '아리랑 레스토랑', '파리바게뜨', '뚝섬 치킨', '맘스터치'],
                'salary_range' => ['hourly', 15, 25],
            ],
            'it' => [
                'titles'       => ['풀스택 개발자 모집', '프론트엔드 개발자 (React)', '백엔드 개발자 (PHP/Python)', '모바일 앱 개발자 구인', 'QA 엔지니어 채용', '데이터 분석가 구합니다', 'DevOps 엔지니어 모집', 'IT 헬프데스크 직원 구인'],
                'companies'    => ['TechKorea Inc', 'Seoul Software', 'K-Digital', 'Hana Tech', 'Pacific Systems', 'Han IT Solutions', 'KoreaTech Labs'],
                'salary_range' => ['yearly', 70000, 150000],
            ],
            'construction' => [
                'titles'       => ['인테리어 기술자 구합니다', '페인터 구인', '전기 기술자 모집', '배관공 채용', '목수 경력자 우대', '타일 기술자 급구', '핸디맨 구합니다', '건설 현장 감독 구인'],
                'companies'    => ['한미 건설', 'K-Build Inc', '동양 인테리어', 'Pacific Construction', '삼성 건설', '하나 인테리어'],
                'salary_range' => ['hourly', 20, 40],
            ],
            'office' => [
                'titles'       => ['사무실 행정직원 구합니다', '경리/회계 직원 모집', '리셉셔니스트 채용', '한영 통번역 구인', '마케팅 담당자 모집', '영업 사원 구합니다', '보험 에이전트 모집', '부동산 어시스턴트 구인'],
                'companies'    => ['한미 회계법인', '코리안 보험', 'K-Real Estate', '서울 CPA', 'Pacific Law Group', '한인 보험센터'],
                'salary_range' => ['monthly', 3000, 6000],
            ],
            'education' => [
                'titles'       => ['한국어 교사 구합니다', '수학/영어 과외 선생님 모집', '피아노 강사 채용', '태권도 사범 구인', '미술 강사 모집', '유치원 교사 구합니다', 'SAT/ACT 튜터 모집', '방과 후 교사 구인'],
                'companies'    => ['한미 학원', '서울 아카데미', 'K-Education Center', '밝은미래 교육원', '한인 주말학교', '세종 한국어학원'],
                'salary_range' => ['hourly', 20, 50],
            ],
            'medical' => [
                'titles'       => ['치과 어시스턴트 구합니다', '한의원 접수 직원 모집', '물리치료사 구인', '간호사 채용', '약국 테크니션 모집', '피부과 직원 구합니다', '한방 침술사 구인'],
                'companies'    => ['한미 치과', '서울 한의원', '동양 한방 클리닉', '코리안 메디컬', '하나 약국', '밝은 눈 안과'],
                'salary_range' => ['hourly', 18, 35],
            ],
            'retail' => [
                'titles'       => ['마트 캐셔 구합니다', '화장품 판매직 모집', '의류 매장 직원 채용', '편의점 알바 구합니다', '셀폰 매장 직원 모집', '꽃집 직원 구합니다', '한인 마트 정육부 구인'],
                'companies'    => ['H마트', '한남체인', '아리랑 마트', 'K-Beauty Shop', '코리아 슈퍼마켓', '한인 플라자'],
                'salary_range' => ['hourly', 15, 22],
            ],
            'beauty' => [
                'titles'       => ['네일 테크니션 구합니다', '헤어 스타일리스트 모집', '속눈썹 연장 시술자 구인', '피부 관리사 채용', '왁싱 전문가 모집', '남성 바버 구합니다'],
                'companies'    => ['뷰티 살롱 서울', 'K-Nail Spa', '아름다운 헤어', 'Pacific Beauty', '한미 네일', '코리안 스파'],
                'salary_range' => ['hourly', 15, 30],
            ],
            'driving' => [
                'titles'       => ['배달 드라이버 구합니다', '무버 드라이버 모집', '셔틀 운전기사 채용', '택시/라이드 드라이버 구인', '트럭 드라이버 모집', '공항 픽업 드라이버 구합니다'],
                'companies'    => ['한인 무빙', 'K-Express Delivery', '코리안 셔틀', 'Pacific Moving Co.', '서울 택배', '한미 물류'],
                'salary_range' => ['hourly', 18, 30],
            ],
            'etc' => [
                'titles'       => ['세탁소 직원 구합니다', '주유소 알바 모집', '창고 작업자 구인', '청소 직원 채용', '주차 관리원 모집', '보안 요원 구합니다', '가사 도우미 구인'],
                'companies'    => ['한미 클리닝', 'K-Laundry', '코리안 서비스', 'Pacific Services', '한인 빌딩 관리'],
                'salary_range' => ['hourly', 15, 22],
            ],
        ];

        $types  = ['full', 'part', 'contract'];
        $cities = [
            ['city' => 'Los Angeles',   'state' => 'CA', 'lat' => 34.0522,  'lng' => -118.2437, 'zip' => '90010'],
            ['city' => 'New York',      'state' => 'NY', 'lat' => 40.7128,  'lng' => -74.0060,  'zip' => '11354'],
            ['city' => 'Chicago',       'state' => 'IL', 'lat' => 41.8781,  'lng' => -87.6298,  'zip' => '60625'],
            ['city' => 'Atlanta',       'state' => 'GA', 'lat' => 33.7490,  'lng' => -84.3880,  'zip' => '30338'],
            ['city' => 'Dallas',        'state' => 'TX', 'lat' => 32.7767,  'lng' => -96.7970,  'zip' => '75006'],
            ['city' => 'Houston',       'state' => 'TX', 'lat' => 29.7604,  'lng' => -95.3698,  'zip' => '77036'],
            ['city' => 'Seattle',       'state' => 'WA', 'lat' => 47.6062,  'lng' => -122.3321, 'zip' => '98104'],
            ['city' => 'San Francisco', 'state' => 'CA', 'lat' => 37.7749,  'lng' => -122.4194, 'zip' => '94112'],
            ['city' => 'Washington',    'state' => 'DC', 'lat' => 38.9072,  'lng' => -77.0369,  'zip' => '22003'],
            ['city' => 'Philadelphia',  'state' => 'PA', 'lat' => 39.9526,  'lng' => -75.1652,  'zip' => '19107'],
        ];

        $contentTemplates = [
            "저희 {company}에서 함께 일할 {title_short}를 찾고 있습니다.\n\n[근무 조건]\n- 근무 형태: {type_ko}\n- 급여: {salary}\n- 근무지: {city}\n\n[우대사항]\n- 경력자 우대\n- 한영 이중언어 가능자 우대\n- 성실하고 책임감 있는 분\n\n[복리후생]\n- 점심 제공\n- 주차 무료\n- 유급 휴가\n\n관심 있으신 분은 연락 주세요.\n이메일: {email}\n전화: {phone}",
            "{company}에서 {title_short}를 급히 모집합니다.\n\n경력 무관, 성실한 분이면 됩니다.\n\n근무지: {city}\n급여: {salary}\n근무 형태: {type_ko}\n\n관심 있으신 분은 아래로 연락 바랍니다.\nTel: {phone}\nEmail: {email}",
            "안녕하세요, {company}입니다.\n\n저희 회사에서 {title_short} 포지션으로 함께 할 인재를 찾습니다.\n\n주요 업무:\n- 해당 분야 실무 담당\n- 고객 상담 및 관리\n- 팀 협업\n\n자격 요건:\n- 관련 경력 1년 이상 (신입도 지원 가능)\n- 한국어/영어 소통 가능\n- 장기 근무 가능자 우대\n\n급여: {salary}\n근무지: {city}\n연락처: {phone}",
        ];

        $typeKo = ['full' => '풀타임', 'part' => '파트타임', 'contract' => '계약직'];

        $now  = now();
        $rows = [];
        $categories = array_keys($categoryJobs);

        for ($i = 0; $i < 300; $i++) {
            $catKey  = $categories[array_rand($categories)];
            $catData = $categoryJobs[$catKey];
            $city    = $cities[array_rand($cities)];
            $type    = $types[array_rand($types)];
            $company = $catData['companies'][array_rand($catData['companies'])];
            $title   = $catData['titles'][array_rand($catData['titles'])];
            $salaryType = $catData['salary_range'][0];
            $salaryMin  = $catData['salary_range'][1];
            $salaryMax  = $catData['salary_range'][2];
            $phone   = '(' . rand(200, 999) . ') ' . rand(200, 999) . '-' . rand(1000, 9999);
            $email   = 'hr@' . strtolower(str_replace([' ', '.'], '', $company)) . '.com';

            $salaryDisplay = $salaryType === 'hourly'
                ? '$' . $salaryMin . ' ~ $' . $salaryMax . '/시간'
                : ($salaryType === 'monthly' ? '$' . number_format($salaryMin) . ' ~ $' . number_format($salaryMax) . '/월' : '$' . number_format($salaryMin) . ' ~ $' . number_format($salaryMax) . '/년');

            $content = str_replace(
                ['{company}', '{title_short}', '{type_ko}', '{salary}', '{city}', '{phone}', '{email}'],
                [$company, preg_replace('/ (구합니다|모집|채용|구인)/', '', $title), $typeKo[$type], $salaryDisplay, $city['city'], $phone, $email],
                $contentTemplates[array_rand($contentTemplates)]
            );

            $actualMin = rand($salaryMin, (int)(($salaryMin + $salaryMax) / 2));
            $actualMax = rand((int)(($salaryMin + $salaryMax) / 2), $salaryMax);

            $rows[] = [
                'user_id'       => $userIds[array_rand($userIds)],
                'title'         => $title,
                'company'       => $company,
                'content'       => $content,
                'category'      => $catKey,
                'type'          => $type,
                'salary_min'    => $actualMin,
                'salary_max'    => $actualMax,
                'salary_type'   => $salaryType,
                'lat'           => round($city['lat'] + rand(-200, 200) / 10000, 7),
                'lng'           => round($city['lng'] + rand(-200, 200) / 10000, 7),
                'city'          => $city['city'],
                'state'         => $city['state'],
                'zipcode'       => $city['zip'],
                'contact_email' => $email,
                'contact_phone' => $phone,
                'is_active'     => rand(0, 100) > 10,
                'expires_at'    => $now->copy()->addDays(rand(7, 60)),
                'view_count'    => rand(5, 300),
                'created_at'    => $now->copy()->subDays(rand(0, 60))->subHours(rand(0, 23)),
                'updated_at'    => $now,
            ];
        }

        foreach (array_chunk($rows, 50) as $chunk) {
            JobPost::insert($chunk);
        }

        $this->command->info('JobSeeder: 300 job posts created');
    }
}
