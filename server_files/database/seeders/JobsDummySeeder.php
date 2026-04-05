<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class JobsDummySeeder extends Seeder
{
    public function run(): void
    {
        $userIds = DB::table('users')->pluck('id')->toArray();
        if (empty($userIds)) {
            $this->command->error('users 테이블에 데이터가 없습니다. FakeUsersSeeder를 먼저 실행하세요.');
            return;
        }

        $this->command->info('구인구직 300개 생성 중...');

        // ── 카테고리별 구인 데이터 ──
        $jobData = [
            // 식당/서빙
            ['title' => '한식당 서버 급구 (Koreatown)', 'company' => '서울식당', 'type' => 'part_time', 'salary' => '$18-22/hr + tips', 'content' => '코리아타운 한식당에서 서버를 모집합니다. 주말 포함 가능하신 분 우대. 경력 무관, 한국어/영어 가능자.'],
            ['title' => '한식 뷔페 주방 보조 구합니다', 'company' => '한가위 뷔페', 'type' => 'full_time', 'salary' => '$16-18/hr', 'content' => '한식 뷔페 주방 보조 구합니다. 아침 6시 출근 가능하신 분. 식사 제공. 경력 우대하지만 초보도 환영합니다.'],
            ['title' => '카페 바리스타 모집', 'company' => '달빛 카페', 'type' => 'part_time', 'salary' => '$17-20/hr', 'content' => '한인타운 카페에서 바리스타를 찾고 있습니다. 커피 제조 경험자 우대. 주 3-5일 근무.'],
            ['title' => 'BBQ 레스토랑 쿡 모집', 'company' => '불꽃 BBQ', 'type' => 'full_time', 'salary' => '$20-25/hr', 'content' => 'Korean BBQ 레스토랑에서 경험 있는 쿡을 모집합니다. 고기 굽기 및 한식 조리 가능자.'],
            ['title' => '일식당 스시 셰프 구합니다', 'company' => '사쿠라', 'type' => 'full_time', 'salary' => '$25-35/hr', 'content' => '스시 셰프 경력 2년 이상. 주 5일 근무. 보험 제공.'],
            ['title' => '베이커리 직원 모집', 'company' => '파리바게뜨', 'type' => 'part_time', 'salary' => '$16-18/hr', 'content' => '한인 베이커리에서 판매 및 제조 보조 직원을 모집합니다. 주말 근무 가능자.'],
            ['title' => '분식집 홀서빙 알바', 'company' => '신전떡볶이', 'type' => 'part_time', 'salary' => '$15-17/hr', 'content' => '분식집 홀서빙 파트타임 구합니다. 평일 저녁 및 주말 가능자.'],

            // 네일샵
            ['title' => '네일 테크니션 경력자 모집', 'company' => 'Luxe Nails', 'type' => 'full_time', 'salary' => '$4000-6000/mo', 'content' => '네일 테크니션 경력자를 모집합니다. 라이센스 필수. 젤, 아크릴 능숙자 우대. 좋은 위치, 안정적인 고객층.'],
            ['title' => '네일샵 리셉셔니스트', 'company' => 'Pretty Nails', 'type' => 'full_time', 'salary' => '$16-18/hr', 'content' => '네일샵 프론트 데스크 직원을 모집합니다. 영어/한국어 가능자. 예약 관리 및 고객 응대.'],
            ['title' => '네일샵 매니저 구합니다', 'company' => 'K-Beauty Nails', 'type' => 'full_time', 'salary' => '$5000-7000/mo', 'content' => '네일샵 운영 매니저를 모집합니다. 영어 능통, 직원 관리 경험 우대.'],

            // 운전/배달
            ['title' => '아마존 배달기사 주당 $1500+', 'company' => 'Amazon DSP', 'type' => 'full_time', 'salary' => '$1500+/wk', 'content' => '아마존 배달 기사 모집. 유효한 운전면허 필수. 주 4-5일 근무. 보험 및 유급 휴가 제공.'],
            ['title' => 'UPS 배달 드라이버', 'company' => 'UPS', 'type' => 'full_time', 'salary' => '$22-28/hr', 'content' => 'UPS 배달 드라이버를 모집합니다. CDL 불필요. 체력 좋으신 분. 주 5일 근무.'],
            ['title' => '한인 물류 배달기사 모집', 'company' => '한진 물류', 'type' => 'full_time', 'salary' => '$20-25/hr', 'content' => '한인 물류 회사에서 배달기사를 모집합니다. 박스 트럭 운전 가능자. 한인마트 배달 위주.'],
            ['title' => '무버(이사) 도우미 구합니다', 'company' => '한인 이사센터', 'type' => 'part_time', 'salary' => '$18-22/hr', 'content' => '이사 도우미를 모집합니다. 체력 좋으신 분. 주말 가능자. 팁 별도.'],
            ['title' => '공항 리무진 드라이버', 'company' => 'LAX 리무진', 'type' => 'contract', 'salary' => '$25-30/hr + tips', 'content' => '공항 픽업/드롭오프 리무진 드라이버를 모집합니다. 깨끗한 DMV 기록 필수.'],

            // 사무직
            ['title' => '한인 법률사무소 사무보조', 'company' => '김앤리 법률사무소', 'type' => 'full_time', 'salary' => '$3500-4500/mo', 'content' => '이민 법률사무소에서 사무보조 직원을 모집합니다. 한국어/영어 가능자. 서류 정리 및 고객 상담.'],
            ['title' => '한인 회계사무소 어시스턴트', 'company' => '정앤박 CPA', 'type' => 'full_time', 'salary' => '$3500-5000/mo', 'content' => '회계사무소 어시스턴트 모집. 회계 지식 있으신 분 우대. 세금 시즌 바쁨.'],
            ['title' => '부동산 사무실 행정직원', 'company' => 'K-Realty', 'type' => 'full_time', 'salary' => '$3000-4000/mo', 'content' => '한인 부동산 사무실에서 행정직원을 모집합니다. MLS 경험자 우대.'],
            ['title' => '보험회사 에이전트 모집', 'company' => '한인 보험', 'type' => 'full_time', 'salary' => '$4000-8000/mo', 'content' => '생명보험/자동차보험 에이전트를 모집합니다. 라이센스 취득 지원. 수수료 높은 편.'],
            ['title' => '한인 여행사 직원 모집', 'company' => '하나투어 미주', 'type' => 'full_time', 'salary' => '$3000-4000/mo', 'content' => '한인 여행사에서 직원을 모집합니다. 항공권 발권 경험 우대. 고객 상담 및 예약 업무.'],

            // 마케팅
            ['title' => '소셜미디어 마케터 모집', 'company' => 'K-Digital', 'type' => 'full_time', 'salary' => '$4000-6000/mo', 'content' => '한인 대상 소셜미디어 마케팅 담당자를 모집합니다. 인스타그램, 유튜브, 틱톡 콘텐츠 제작.'],
            ['title' => '유튜브 콘텐츠 크리에이터', 'company' => '한인 미디어', 'type' => 'freelance', 'salary' => '$3000-5000/mo', 'content' => '한인 커뮤니티 관련 유튜브 콘텐츠를 제작할 크리에이터를 찾습니다. 영상 편집 가능자.'],
            ['title' => '그래픽 디자이너 프리랜서', 'company' => 'Creative K', 'type' => 'freelance', 'salary' => '$30-50/hr', 'content' => '한인 비즈니스 광고물 디자인 프리랜서를 모집합니다. Photoshop, Illustrator 필수.'],

            // IT
            ['title' => '풀스택 개발자 채용', 'company' => 'K-Tech', 'type' => 'full_time', 'salary' => '$6000-8000/mo', 'content' => 'React/Node.js 풀스택 개발자를 모집합니다. 경력 2년 이상. 리모트 근무 가능.'],
            ['title' => 'QA 테스터 모집', 'company' => 'TestKorea', 'type' => 'contract', 'salary' => '$25-35/hr', 'content' => '한국어 앱/웹 QA 테스터를 모집합니다. 한국어 능통자 필수. 원격 근무.'],
            ['title' => '워드프레스 웹사이트 개발', 'company' => 'K-Web', 'type' => 'freelance', 'salary' => '$500-2000/project', 'content' => '한인 비즈니스 웹사이트 제작 프리랜서를 모집합니다. 워드프레스 경험 필수.'],
            ['title' => 'IT 서포트 기술자', 'company' => '한인 IT', 'type' => 'full_time', 'salary' => '$4000-5500/mo', 'content' => '한인 사무실 IT 서포트 담당자를 모집합니다. 네트워크, PC 수리 가능자.'],

            // 건설
            ['title' => '페인터(도장) 경력자 구합니다', 'company' => '한인 페인팅', 'type' => 'full_time', 'salary' => '$22-30/hr', 'content' => '실내/외 페인팅 경력자를 모집합니다. 차량 보유자 우대. 주 5-6일 근무.'],
            ['title' => '핸디맨 구합니다', 'company' => 'K-Fix', 'type' => 'contract', 'salary' => '$25-35/hr', 'content' => '집수리 전반 가능한 핸디맨을 모집합니다. 전기, 배관, 목공 기본 가능자.'],
            ['title' => '타일/바닥공사 기사', 'company' => '한인 건설', 'type' => 'full_time', 'salary' => '$25-35/hr', 'content' => '타일 및 바닥재 시공 경력자를 모집합니다. 차량 및 도구 보유자 우대.'],

            // 의료
            ['title' => '한인 치과 치위생사 모집', 'company' => '김치과', 'type' => 'full_time', 'salary' => '$5000-7000/mo', 'content' => '치위생사 라이센스 보유자를 모집합니다. 한국어/영어 가능자. 주 4-5일 근무.'],
            ['title' => '한의원 리셉셔니스트', 'company' => '서울한의원', 'type' => 'full_time', 'salary' => '$3000-3500/mo', 'content' => '한의원 프론트 데스크 직원을 모집합니다. 보험 청구 경험 우대.'],
            ['title' => 'CNA 간호조무사 모집', 'company' => '한인 요양원', 'type' => 'full_time', 'salary' => '$18-22/hr', 'content' => 'CNA 자격증 소유자를 모집합니다. 한인 노인 케어. 야간 근무 가능자 우대.'],
            ['title' => '약국 테크니션', 'company' => '한인 약국', 'type' => 'full_time', 'salary' => '$18-22/hr', 'content' => '약국 테크니션을 모집합니다. 라이센스 보유자. 한국어/영어 가능자.'],

            // 교육
            ['title' => '한국어 강사 모집', 'company' => '한글학교', 'type' => 'part_time', 'salary' => '$25-35/hr', 'content' => '주말 한국어 강사를 모집합니다. 아이들 대상 수업 경험자 우대.'],
            ['title' => '수학/영어 과외 선생님', 'company' => '한인 학원', 'type' => 'part_time', 'salary' => '$30-50/hr', 'content' => '중고등학생 수학/영어 과외 선생님을 모집합니다. 대학 졸업자.'],
            ['title' => '피아노 선생님 구합니다', 'company' => '예음 음악학원', 'type' => 'part_time', 'salary' => '$35-50/hr', 'content' => '피아노 레슨 선생님을 모집합니다. 음대 졸업 또는 관련 경력자.'],
            ['title' => '태권도 사범 모집', 'company' => '한인 태권도장', 'type' => 'full_time', 'salary' => '$3500-5000/mo', 'content' => '태권도 유단자(3단 이상)를 모집합니다. 아이들 지도 가능자.'],

            // 기타
            ['title' => '세탁소 직원 모집', 'company' => '한인 클리닝', 'type' => 'full_time', 'salary' => '$16-18/hr', 'content' => '드라이클리닝 경험자 우대. 주 5일 근무. 간단한 봉재 가능자 우대.'],
            ['title' => '꽃집 플로리스트', 'company' => '한인 플라워', 'type' => 'part_time', 'salary' => '$17-20/hr', 'content' => '꽃꽂이 가능한 분을 모집합니다. 주말 행사 위주. 배달 가능자 우대.'],
            ['title' => '미용사 모집합니다', 'company' => '준오 헤어', 'type' => 'full_time', 'salary' => '$4000-7000/mo', 'content' => '코스메톨로지 라이센스 보유자. 한인 고객 위주. 경력 1년 이상.'],
            ['title' => '애완동물 그루머', 'company' => '멍멍 그루밍', 'type' => 'full_time', 'salary' => '$3500-5000/mo', 'content' => '반려동물 그루밍 경험자를 모집합니다. 소형견 위주. 라이센스 우대.'],
            ['title' => '인쇄소 직원 모집', 'company' => '한인 프린팅', 'type' => 'full_time', 'salary' => '$17-20/hr', 'content' => '인쇄기 운용 경험자 또는 디자인 가능자를 모집합니다. Adobe 프로그램 활용.'],
            ['title' => '통역/번역 프리랜서', 'company' => 'K-Translation', 'type' => 'freelance', 'salary' => '$30-50/hr', 'content' => '한영/영한 통역 및 번역 프리랜서를 모집합니다. 의료/법률 통역 경험자 우대.'],
            ['title' => '호텔 프론트 데스크', 'company' => 'LA Hotel', 'type' => 'full_time', 'salary' => '$18-22/hr', 'content' => '호텔 프론트 데스크 직원을 모집합니다. 영어 능통. 야간 교대 가능자.'],
            ['title' => '청소업체 직원 모집', 'company' => '한인 청소', 'type' => 'full_time', 'salary' => '$16-20/hr', 'content' => '주거/상업 공간 청소 직원을 모집합니다. 차량 보유자 우대. 팁 별도.'],
        ];

        $regions = ['Los Angeles', 'New York', 'Atlanta', 'Chicago', 'Seattle', 'Dallas', 'Houston', 'San Francisco', 'Boston', 'Miami', 'San Jose', 'Virginia', 'New Jersey', 'Denver', 'Portland'];
        $addresses = [
            'Los Angeles' => ['3000 W Olympic Blvd', '621 S Western Ave', '3500 W 6th St', '333 S Alameda St', '4001 Wilshire Blvd'],
            'New York' => ['149-06 41st Ave, Flushing', '32 W 32nd St, Manhattan', '150-28 Northern Blvd', '35-20 Farrington St'],
            'Atlanta' => ['5302 Buford Hwy', '3242 Steve Reynolds Blvd', '2550 Pleasant Hill Rd'],
            'Chicago' => ['4747 N Western Ave', '3346 W Bryn Mawr Ave', '5000 N Lincoln Ave'],
            'Seattle' => ['2320 S Jackson St', '1032 S Jackson St', '520 6th Ave S'],
            'Dallas' => ['2625 Old Denton Rd', '1100 Royal Ln', '2540 Royal Ln'],
            'Houston' => ['1302 Blalock Rd', '9896 Bellaire Blvd', '1005 Blalock Rd'],
            'San Francisco' => ['2370 Noriega St', '1531 Clement St', '3439 Geary Blvd'],
            'Boston' => ['1 Union St', '86 Kneeland St', '14 Tyler St'],
            'Miami' => ['155 S Miami Ave', '120 NE 27th St', '230 NE 4th St'],
            'San Jose' => ['3150 El Camino Real', '1530 Hamilton Ave', '2855 Stevens Creek Blvd'],
            'Virginia' => ['7048 Spring Garden Dr', '8515 Lee Hwy', '3217 Columbia Pike'],
            'New Jersey' => ['1585 Palisade Ave', '300 Broad Ave', '201 Main St'],
            'Denver' => ['2080 S Havana St', '10667 E Garden Dr', '3333 S Tamarac Dr'],
            'Portland' => ['6600 SW Beaverton-Hillsdale', '4236 SE Belmont St', '2348 SE Hawthorne'],
        ];
        $phoneNumbers = [];
        for ($i = 0; $i < 50; $i++) {
            $phoneNumbers[] = '(' . rand(200, 999) . ') ' . rand(200, 999) . '-' . str_pad(rand(0, 9999), 4, '0', STR_PAD_LEFT);
        }
        $emails = [];
        for ($i = 0; $i < 50; $i++) {
            $emailNames = ['hr', 'jobs', 'hiring', 'recruit', 'apply', 'info', 'contact', 'work'];
            $emailDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'naver.com', 'kakao.com'];
            $emails[] = $emailNames[array_rand($emailNames)] . rand(100, 999) . '@' . $emailDomains[array_rand($emailDomains)];
        }

        $now = Carbon::now();
        $rows = [];

        for ($i = 0; $i < 300; $i++) {
            $job = $jobData[$i % count($jobData)];
            $region = $regions[array_rand($regions)];
            $regionAddresses = $addresses[$region] ?? ['123 Main St'];
            $address = $regionAddresses[array_rand($regionAddresses)] . ', ' . $region;

            $daysAgo = rand(0, 90);
            $hour = rand(7, 23);
            $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute(rand(0, 59))->setSecond(rand(0, 59));

            $deadlineDays = rand(14, 60);
            $deadline = $createdAt->copy()->addDays($deadlineDays);
            $status = $deadline->lt($now) ? 'closed' : 'active';

            $rows[] = [
                'user_id'       => $userIds[array_rand($userIds)],
                'title'         => $job['title'],
                'content'       => $job['content'] . "\n\n위치: {$address}\n급여: {$job['salary']}\n\n관심 있으신 분은 연락 주세요!",
                'company_name'  => $job['company'],
                'contact_email' => $emails[array_rand($emails)],
                'contact_phone' => $phoneNumbers[array_rand($phoneNumbers)],
                'region'        => $region,
                'address'       => $address,
                'job_type'      => $job['type'],
                'salary_range'  => $job['salary'],
                'deadline'      => $deadline->format('Y-m-d'),
                'is_pinned'     => false,
                'view_count'    => rand(30, 1500),
                'status'        => $status,
                'created_at'    => $createdAt,
                'updated_at'    => $createdAt,
            ];
        }

        // 50개씩 chunk insert
        foreach (array_chunk($rows, 50) as $chunk) {
            DB::table('job_posts')->insert($chunk);
        }

        $this->command->info('구인구직 300개 생성 완료!');
    }
}
