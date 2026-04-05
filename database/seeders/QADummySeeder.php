<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class QADummySeeder extends Seeder
{
    public function run(): void
    {
        $userIds = DB::table('users')->pluck('id')->toArray();
        if (empty($userIds)) {
            $this->command->error('users 테이블에 데이터가 없습니다. FakeUsersSeeder를 먼저 실행하세요.');
            return;
        }

        $this->command->info('Q&A 질문 300개 생성 중...');

        $categorySlugs = ['immigration', 'tax', 'medical', 'jobs', 'realestate', 'car', 'education', 'business', 'finance', 'general'];

        // ── 카테고리별 질문 제목 풀 ──
        $questionsByCategory = [
            'immigration' => [
                '영주권 갱신 절차가 어떻게 되나요?', 'H1B 비자 추첨 확률이 어느 정도인가요?',
                'F1에서 H1B로 변경하는 방법', 'I-485 접수 후 얼마나 걸리나요?',
                '시민권 인터뷰 질문 리스트', 'EAD 카드 갱신 타이밍', 'DACA 갱신 절차 문의',
                '영주권 스탬핑 vs I-485 차이점', '배우자 영주권 초청 기간', 'J1 비자 2년 룰 면제 방법',
                'EB2 NIW 셀프 청원 가능한가요?', 'B1/B2 비자로 체류 연장', '이민국 면접 준비 방법',
                'K1 비자 처리 기간이 얼마나 되나요?', '추방 위험 상황 대처법',
                'L1 비자에서 영주권으로', '시민권 시험 100문제 어디서 볼 수 있나요?',
                '영주권자 해외 체류 기간 제한', 'TPS 신청 자격 요건', 'VAWA 자가 청원',
                '영주권 분실 시 재발급', '여행허가서 신청 후 해외여행', 'I-130 승인 후 다음 단계',
                'H4 EAD 신청 조건', '비자 거절 후 재신청 가능한가요?',
                '이민 변호사 비용 보통 얼마인가요?', 'USCIS 케이스 상태 확인하는 법',
                '시민권 포기 절차', '영주권 10년 갱신 준비물', 'O1 비자 자격 요건',
            ],
            'tax' => [
                '한국 송금 세금 보고 해야하나요?', 'FBAR 보고 안하면 어떻게 되나요?',
                '한국 부동산 소득 미국 세금보고', 'LLC vs S-Corp 세금 차이',
                'W2 vs 1099 어떤 게 유리한가요?', '자녀 세금 공제 받는 방법',
                'Turbotax로 직접 세금보고 가능한가요?', '세금보고 연장 신청 방법',
                'ITIN 번호 받는 방법', '프리랜서 세금 계산법', '한미 조세조약 내용',
                '양도소득세 면제 조건', '상속세 미국 vs 한국', '비트코인 세금 보고 방법',
                'HSA 세금 혜택 활용법', '529 플랜 세금 공제', 'IRA 세금 공제 한도',
                '소규모 사업 경비 처리법', '세금보고 실수했을 때 수정 방법',
                '미국 세금보고 기본 가이드', 'CPA vs EA 어떤 전문가가 좋나요?',
                '재택근무 홈오피스 공제', '기부금 세금 공제 한도', '부부 공동보고 vs 개별보고',
                '자영업자 분기별 세금 납부', '미국 비거주자 세금보고',
                '한국 연금 수령시 미국 세금', '주식 매매 세금', '1099-K 받았을 때 처리법',
                '세금 감사 대비 방법',
            ],
            'medical' => [
                '건강보험 없이 응급실 가면?', 'Marketplace 보험 vs 직장 보험',
                '치과 보험 추천해주세요', '한인 가정의학과 추천', '임신 출산 보험 혜택',
                'Medicaid 자격 요건', 'COBRA 보험 연장', '시력 검사 비용',
                '한의원 미국에서 보험 적용되나요?', '정신건강 상담 받고 싶은데',
                '미국 약국 처방전 받는 법', '의료비 할부 납부 가능한가요?',
                'FSA vs HSA 차이점', '소아과 예방접종 스케줄', '미국 건강검진 어디서 받나요?',
                '응급실 vs 어전트케어 차이', '한국에서 약 가져올 수 있나요?',
                '의료 통역 서비스 있나요?', '한인 심리상담사 추천', '무보험자 의료비 할인 방법',
                '오바마케어 신청 기간', '치과 치료 비용 평균', '피부과 추천해주세요',
                '한방 치료 미국에서 인정되나요?', '물리치료 보험 적용 여부',
                '코로나 후유증 치료', '성인 예방접종 필요한 것들', '안과 검진 비용',
                '한인 정형외과 있나요?', '약값 절약하는 방법',
            ],
            'jobs' => [
                '이력서 작성법 미국 스타일', 'LinkedIn 프로필 최적화 방법',
                'OPT 기간 중 취업 팁', '미국 연봉 협상 어떻게 하나요?',
                'H1B 스폰서해주는 회사 찾기', '원격 근무 가능한 직종',
                '한인 취업 박람회 일정', '미국 면접 자주 나오는 질문',
                '직장 내 인종차별 대처법', '퇴직금 401K 어떻게 하나요?',
                '이직 타이밍 조언', '소규모 회사 vs 대기업 장단점',
                '미국 직장 문화 적응 팁', 'IT 분야 취업 전망', '간호사 미국 취업 방법',
                '부업으로 뭐하시나요?', 'Gig Economy 참여 방법', '재택근무 생산성 올리기',
                '미국 직장 복지 혜택 비교', '매니저와 갈등 해결법',
                '네트워킹 효과적으로 하는 법', '포트폴리오 준비 방법',
                '기술 면접 준비 방법', '미국 인턴십 찾는 방법', '직장 영어 이메일 작성법',
                '미국 최저임금 주별 정리', '실업수당 신청 방법', '직장 내 승진 전략',
                '프리랜서로 전환하기', '미국 노동법 기본 상식',
            ],
            'realestate' => [
                '첫 집 구매 과정 A to Z', '렌트비 너무 올랐는데 협상 가능한가요?',
                '룸메이트 구할 때 주의할 점', '모기지 금리 비교 방법',
                '다운페이먼트 얼마 준비해야 하나요?', 'FHA 론 vs Conventional 론',
                '집 구매 시 클로징 비용', '홈인스펙션 꼭 해야하나요?',
                '부동산 에이전트 수수료', '렌트 계약서 확인할 점',
                '집값 언제 내려갈까요?', 'HOA 비용 확인 방법', '집수리 업체 추천',
                '재융자 타이밍', '투자용 부동산 구매', '학군 확인하는 방법',
                '월세 vs 집구매 비교', 'Escrow 과정 설명', '타이틀 보험이 뭔가요?',
                '집주인 권리와 의무', '임차인 권리 보호법', '서브렛 가능한가요?',
                '미국 아파트 렌트 절차', '크레딧 점수 몇점이면 집구매 가능?',
                '한인 부동산 에이전트 추천', '집 팔 때 스테이징 필요한가요?',
                '콘도 vs 하우스 장단점', 'VA 론 자격 요건', '부동산 세금 감면',
                '이사 견적 비교 방법',
            ],
            'car' => [
                'DMV 필기시험 한국어로 가능한가요?', '자동차 보험 저렴하게 가입하는 법',
                '중고차 딜러 vs 개인거래', '자동차 리스 장단점',
                '운전면허 시험 코스 팁', '교통 위반 벌금 납부 방법',
                '자동차 등록 갱신', '사고 나면 어떻게 해야 하나요?',
                'DUI 처벌 수준', '차 정비 어디서 해야 저렴한가요?',
                '신차 구매 협상 팁', 'Carfax 리포트 꼭 봐야 하나요?',
                '전기차 보조금 받는 법', '타이어 교체 시기', '오일 체인지 주기',
                '자동차 보험 클레임 절차', '한국 면허 미국 교환 가능?',
                '겨울 운전 안전 팁', '톨 게이트 미납 시', '주차 위반 대처법',
                '차량 타이틀 분실', '캘리포니아 스모그 체크', '운전면허 갱신 방법',
                '렌터카 보험 필요한가요?', 'AAA 멤버십 혜택',
                '차 살 때 세금 계산법', '무보험 운전 걸리면', '국제 운전면허증 유효기간',
                '자동차 리콜 확인 방법', '교통사고 합의 과정',
            ],
            'education' => [
                '아이 학교 등록 서류가 뭐가 필요한가요?', '미국 대학 입시 준비',
                'SAT vs ACT 차이', '학자금 보조 신청 방법', '홈스쿨링 장단점',
                '사립학교 vs 공립학교', '유치원 입학 나이', 'ESL 프로그램 추천',
                '대학 장학금 찾는 방법', '과외 선생님 구하기', '한국학교 등록',
                '학교 급식 프로그램', '특수교육 서비스', '대학원 지원 GRE 필요한가요?',
                'AP 수업 몇 개 들어야 하나요?', '한인 학원 추천', '여름 캠프 프로그램',
                '영재 프로그램 입학', '대학 전공 선택 고민', '유학생 보험',
                '커뮤니티 칼리지 장단점', '편입 절차', '한국 학력 인정 방법',
                'MBA 프로그램 추천', '코딩 부트캠프 경험담', 'STEM 전공 취업 전망',
                '자녀 이중언어 교육', '미국 고등학교 졸업 요건', '대학 기숙사 생활',
                '한국 대학 vs 미국 대학',
            ],
            'business' => [
                'LLC 설립 비용과 절차', '소규모 비즈니스 세금', '식당 오픈 허가 절차',
                '사업자 등록 방법', '프랜차이즈 창업 비용', 'E2 비자로 사업 시작',
                '비즈니스 플랜 작성법', '소규모 대출 받는 방법', 'SBA 론 자격 요건',
                '비즈니스 보험 종류', '직원 고용 시 주의사항', '워커스 컴프 보험',
                '한인 상공회의소 가입', '온라인 쇼핑몰 시작하기', 'Amazon 셀러 되는 법',
                '음식 트럭 창업', '네일샵 오픈 절차', '부동산 에이전트 자격증',
                '프리랜서 사업자 등록', '수출입 사업 시작법', 'DBA 등록이란',
                'EIN 번호 받는 법', '비즈니스 은행 계좌 추천', '한인 타운 상가 임대',
                '사업 파트너십 주의점', '프랜차이즈 vs 독립 창업', '마케팅 전략 조언',
                '소셜미디어 마케팅', '사업 실패 후 대처법',
            ],
            'finance' => [
                '크레딧 점수 올리는 확실한 방법', '주식 투자 초보 가이드',
                '401K 매칭 최대로 받는 법', 'Roth IRA vs Traditional IRA',
                '미국 은행 계좌 추천', '크레딧 카드 추천', '학자금 대출 상환 전략',
                '비상금 얼마나 모아야 하나요?', '미국에서 한국으로 송금 방법',
                '환율 좋을 때 바꾸는 방법', '부동산 투자 시작하기', 'ETF vs 개별주식',
                '은퇴 준비 언제부터?', '생명보험 필요한가요?', '자녀 대학 저축 방법',
                '긴급 자금 마련', '부채 상환 전략', '재정 계획 세우기',
                '미국 연금 수령 나이', '소셜 시큐리티 베네핏', '상속 계획 세우기',
                '고금리 저축 계좌 추천', 'CD 투자 장단점', '부동산 리츠(REIT) 투자',
                '암호화폐 투자 주의점', '인플레이션 대비 전략', '보험 정리 방법',
                '재정 상담사 추천', '신용카드 빚 탈출법', '경제적 자유 달성 방법',
            ],
            'general' => [
                '미국에서 한국 택배 보내는 방법', '반려동물 입양 절차',
                '미국에서 결혼식 준비', '이혼 절차 미국에서', '한인 교회 추천',
                '미국 장례 절차', '한국 귀국 준비 체크리스트', '미국 시민 의무',
                '이웃 분쟁 해결 방법', '아파트 소음 문제', '미국 선거 투표 방법',
                '미국 여행 추천지', '한인 변호사 추천', '무료 법률 상담 받는 곳',
                '한인 커뮤니티 활동', '자원봉사 기회', '한국 음식 배달 서비스',
                '미국 우편 시스템 이해', '인터넷/케이블 설치', '집 보안 시스템',
                '미국에서 한국 전자제품 사용', '여권 갱신 절차', '한국 방문 시 필요한 것',
                '미국 공휴일 정리', '재활용 방법', '자전거 통근 가능한가요?',
                '한인 노인 복지 서비스', '이민자 무료 영어교실', '미국 반려동물 병원 비용',
                '한인 미용실 추천',
            ],
        ];

        // ── 답변 내용 풀 ──
        $answerTemplates = [
            "제가 아는 범위에서 답변드릴게요.\n\n{answer_detail}\n\n더 궁금하신 점 있으시면 편하게 질문해주세요!",
            "저도 비슷한 경험이 있어서 도움이 될 것 같아요.\n\n{answer_detail}\n\n혹시 다른 분들도 추가 정보 있으시면 공유해주세요.",
            "{answer_detail}\n\n이건 제 개인적인 경험이라 상황에 따라 다를 수 있어요. 전문가 상담도 추천드립니다.",
            "좋은 질문이세요! 많은 분들이 궁금해하시는 부분이에요.\n\n{answer_detail}\n\n도움이 됐으면 좋겠습니다!",
            "이 부분에 대해 최근에 알아봤었어요.\n\n{answer_detail}\n\n참고하시되, 최신 정보는 공식 사이트에서 확인하세요.",
            "{answer_detail}\n\n저도 처음엔 몰랐는데 경험하면서 배운 것들이에요. 화이팅!",
        ];

        $answerDetails = [
            '기본적으로 해당 기관 공식 웹사이트에서 최신 정보를 확인하시는 것이 가장 정확합니다. 제가 경험한 바로는 보통 2-3개월 정도 소요되었습니다.',
            '저는 한인 전문가를 통해 처리했는데 비용은 좀 들었지만 확실하게 해결됐어요. 직접 하시려면 서류 준비가 중요합니다.',
            '이 경우에는 먼저 자격 요건을 확인하셔야 해요. 주마다 규정이 다를 수 있으니 본인 거주 주의 법률을 확인하세요.',
            '제 경험상 미리 준비하면 훨씬 수월해요. 필요 서류 목록을 만들고 하나씩 체크하면서 진행하시면 됩니다.',
            '온라인으로 신청 가능하고, 처리 기간은 보통 4-8주 정도 걸립니다. 급하시면 프리미엄 서비스도 있어요.',
            '한인 커뮤니티에서 경험자분들 의견을 많이 들어보세요. 케이스바이케이스라서 다양한 경험을 참고하는 게 좋아요.',
            '저는 이 방법으로 해결했습니다. 첫째 온라인으로 예약하고, 둘째 필요 서류 준비하고, 셋째 당일 일찍 가서 대기하시면 됩니다.',
            '비용 면에서 보면 직접 하는 것이 저렴하지만 시간과 노력이 많이 들어요. 전문가에게 맡기면 편하지만 수수료가 있죠.',
            '이건 상황에 따라 다른데요, 보통의 경우에는 문제없이 진행됩니다. 다만 특수한 경우에는 추가 서류가 필요할 수 있어요.',
            '최근에 직접 해봤는데 생각보다 간단했어요. 웹사이트에 가이드가 잘 되어 있으니 따라하시면 됩니다.',
            '한인 분들이 많이 이용하는 업체가 있는데 가격도 합리적이고 한국어 지원도 됩니다.',
            '여러 곳에 견적을 받아보시는 것을 추천합니다. 가격 차이가 꽤 크거든요.',
        ];

        $now = Carbon::now();
        $questionRows = [];
        $questionIndex = 0;

        for ($i = 0; $i < 300; $i++) {
            $slug = $categorySlugs[$i % count($categorySlugs)];
            $questionsPool = $questionsByCategory[$slug];
            $title = $questionsPool[$questionIndex % count($questionsPool)];
            if (($i + 1) % count($categorySlugs) === 0) $questionIndex++;

            $isResolved = rand(1, 100) <= 40;
            $pointReward = rand(1, 100) <= 50 ? 0 : rand(10, 100);

            $daysAgo = rand(0, 90);
            $hour = rand(7, 23);
            $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute(rand(0, 59))->setSecond(rand(0, 59));

            $contentTemplate = [
                "안녕하세요. {$title}에 대해서 질문드립니다.\n\n미국에서 생활하면서 이 부분이 궁금했는데 주변에 물어볼 사람이 없어서 여기에 올립니다. 경험 있으신 분들 답변 부탁드려요!",
                "{$title}\n\n최근에 이 상황에 처했는데 어떻게 해야 할지 모르겠어요. 비슷한 경험 있으신 분들 조언 부탁합니다. 자세한 내용도 알려주시면 감사하겠습니다.",
                "질문이 있어서 글 올립니다.\n\n{$title} 관련해서 인터넷으로 찾아봤는데 정보가 너무 많고 뭐가 맞는지 헷갈려요. 실제 경험하신 분들 답변 부탁드립니다!",
                "급하게 질문드립니다.\n\n{$title}에 대해 잘 아시는 분 계시면 도움 부탁드려요. 기한이 얼마 안 남아서 빨리 알아야 하는데 혼자서는 한계가 있네요.",
            ];

            $questionRows[] = [
                'user_id'            => $userIds[array_rand($userIds)],
                'category_slug'      => $slug,
                'title'              => $title,
                'content'            => $contentTemplate[array_rand($contentTemplate)],
                'point_reward'       => $pointReward,
                'accepted_answer_id' => null,
                'is_resolved'        => $isResolved,
                'view_count'         => rand(30, 2000),
                'answer_count'       => 0, // 나중에 업데이트
                'recommend_count'    => rand(0, 30),
                'resolved_at'        => $isResolved ? $createdAt->copy()->addDays(rand(1, 14)) : null,
                'created_at'         => $createdAt,
                'updated_at'         => $createdAt,
            ];
        }

        // 50개씩 chunk insert
        foreach (array_chunk($questionRows, 50) as $chunk) {
            DB::table('qa_questions')->insert($chunk);
        }
        $this->command->info('질문 300개 생성 완료.');

        // ── 답변 900개 ──
        $this->command->info('Q&A 답변 900개 생성 중...');

        $questionIds = DB::table('qa_questions')->orderByDesc('id')->limit(300)->get(['id', 'user_id', 'is_resolved'])->toArray();

        $answerRows = [];
        $questionAnswerCounts = [];
        $totalAnswers = 0;

        foreach ($questionIds as $q) {
            $numAnswers = rand(1, 5);
            $questionAnswerCounts[$q->id] = ['count' => $numAnswers, 'user_id' => $q->user_id, 'is_resolved' => $q->is_resolved];
            $totalAnswers += $numAnswers;
        }

        // 900개에 맞추기
        while ($totalAnswers < 900) {
            $randQ = $questionIds[array_rand($questionIds)];
            if ($questionAnswerCounts[$randQ->id]['count'] < 5) {
                $questionAnswerCounts[$randQ->id]['count']++;
                $totalAnswers++;
            }
        }
        while ($totalAnswers > 900) {
            $randQ = $questionIds[array_rand($questionIds)];
            if ($questionAnswerCounts[$randQ->id]['count'] > 1) {
                $questionAnswerCounts[$randQ->id]['count']--;
                $totalAnswers--;
            }
        }

        foreach ($questionAnswerCounts as $qId => $info) {
            $otherUsers = array_values(array_filter($userIds, fn($uid) => $uid !== $info['user_id']));
            if (empty($otherUsers)) $otherUsers = $userIds;

            for ($a = 0; $a < $info['count']; $a++) {
                $template = $answerTemplates[array_rand($answerTemplates)];
                $detail = $answerDetails[array_rand($answerDetails)];
                $content = str_replace('{answer_detail}', $detail, $template);

                $isAccepted = ($info['is_resolved'] && $a === 0); // resolved 질문의 첫 번째 답변만 accepted

                $daysAgo = rand(0, 85);
                $hour = rand(7, 23);
                $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute(rand(0, 59))->setSecond(rand(0, 59));

                $answerRows[] = [
                    'question_id' => $qId,
                    'user_id'     => $otherUsers[array_rand($otherUsers)],
                    'content'     => $content,
                    'is_accepted' => $isAccepted,
                    'like_count'  => rand(0, 30),
                    'created_at'  => $createdAt,
                    'updated_at'  => $createdAt,
                ];
            }
        }

        // 50개씩 chunk insert
        foreach (array_chunk($answerRows, 50) as $chunk) {
            DB::table('qa_question_answers')->insert($chunk);
        }

        // answer_count 업데이트
        foreach ($questionAnswerCounts as $qId => $info) {
            DB::table('qa_questions')->where('id', $qId)->update(['answer_count' => $info['count']]);
        }

        // accepted_answer_id 업데이트
        $resolvedQuestions = DB::table('qa_questions')
            ->where('is_resolved', true)
            ->orderByDesc('id')
            ->limit(300)
            ->pluck('id');

        foreach ($resolvedQuestions as $qId) {
            $acceptedAnswerId = DB::table('qa_question_answers')
                ->where('question_id', $qId)
                ->where('is_accepted', true)
                ->value('id');
            if ($acceptedAnswerId) {
                DB::table('qa_questions')->where('id', $qId)->update(['accepted_answer_id' => $acceptedAnswerId]);
            }
        }

        $this->command->info('답변 ' . count($answerRows) . '개 생성 완료.');
        $this->command->info('QADummySeeder 완료!');
    }
}
