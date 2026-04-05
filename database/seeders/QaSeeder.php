<?php

namespace Database\Seeders;

use App\Models\QaCategory;
use App\Models\QaPost;
use App\Models\QaAnswer;
use App\Models\User;
use Illuminate\Database\Seeder;

class QaSeeder extends Seeder
{
    public function run(): void
    {
        $userIds     = User::pluck('id')->toArray();
        $categoryIds = QaCategory::pluck('id', 'name')->toArray();
        if (empty($userIds) || empty($categoryIds)) {
            $this->command->warn('QaSeeder: users or categories missing, skipping.');
            return;
        }

        $questions = [
            // 이민/비자
            ['cat' => '이민/비자', 'title' => 'H1B 비자 추첨 결과 언제 나오나요?', 'content' => '올해 H1B 비자를 신청했는데 추첨 결과가 언제 나오는지 궁금합니다. 작년에 신청하셨던 분들 경험 공유해 주시면 감사하겠습니다.'],
            ['cat' => '이민/비자', 'title' => '영주권 신청 후 대기 시간이 얼마나 되나요?', 'content' => 'EB-2 카테고리로 영주권을 신청했습니다. 현재 대기 시간이 얼마나 되는지 최근 경험이 있으신 분 계신가요?'],
            ['cat' => '이민/비자', 'title' => '시민권 시험 준비 어떻게 하셨나요?', 'content' => '시민권 인터뷰가 한 달 후인데 시험 준비를 어떻게 해야 할지 막막합니다. 합격하신 분들의 팁을 듣고 싶습니다.'],
            ['cat' => '이민/비자', 'title' => '부모님 초청 비자 (IR-5) 소요 시간', 'content' => '시민권자로서 부모님을 초청하려고 합니다. 현재 처리 시간이 얼마나 걸리나요?'],
            ['cat' => '이민/비자', 'title' => 'DACA 갱신 절차가 변경되었나요?', 'content' => 'DACA 갱신을 해야 하는데 최근 절차가 변경되었다고 들었습니다. 최신 정보를 아시는 분 계신가요?'],

            // 법률
            ['cat' => '법률', 'title' => '교통사고 후 보험 처리 절차가 궁금합니다', 'content' => '어제 교통사고가 났는데 상대방 과실입니다. 보험 처리 절차를 어떻게 해야 하나요? 변호사를 선임해야 할까요?'],
            ['cat' => '법률', 'title' => '세입자 퇴거 통보 기한이 어떻게 되나요?', 'content' => '캘리포니아에서 렌트 중인데 갑자기 퇴거 통보를 받았습니다. 법적으로 최소 얼마 전에 통보해야 하나요?'],
            ['cat' => '법률', 'title' => '스몰 클레임 소송 절차 알려주세요', 'content' => '이웃과 분쟁이 있어서 스몰 클레임을 생각하고 있습니다. 진행 절차와 비용이 어떻게 되나요?'],

            // 세금/회계
            ['cat' => '세금/회계', 'title' => '프리랜서 세금 보고 어떻게 하나요?', 'content' => '올해 처음으로 프리랜서로 일했는데 세금 보고를 어떻게 해야 하나요? 1099 폼을 받았는데 어떤 공제를 받을 수 있나요?'],
            ['cat' => '세금/회계', 'title' => '한국에 있는 부동산 미국 세금 보고 해야 하나요?', 'content' => '한국에 아파트가 하나 있는데 미국 세금 보고 시 신고해야 하나요? FBAR 보고도 해야 하나요?'],
            ['cat' => '세금/회계', 'title' => '자녀 세금 공제(Child Tax Credit) 받는 방법', 'content' => '올해 아이가 태어났는데 Child Tax Credit은 어떻게 받나요? SSN이 필요한가요?'],

            // 부동산
            ['cat' => '부동산', 'title' => '첫 주택 구매 시 다운페이먼트는 얼마가 적당한가요?', 'content' => '생애 첫 주택을 구매하려고 합니다. 다운페이먼트를 20% 해야 하나요? FHA 론도 괜찮나요?'],
            ['cat' => '부동산', 'title' => 'HOA 비용이 너무 비싼데 정상인가요?', 'content' => '콘도를 보고 있는데 HOA가 월 $500입니다. 이게 정상적인 가격인가요? HOA에 뭐가 포함되어 있나요?'],
            ['cat' => '부동산', 'title' => '렌트 계약서에 반드시 포함해야 할 내용', 'content' => '처음으로 방을 렌트하려는데 계약서에 반드시 확인해야 할 사항이 뭐가 있나요?'],

            // 자동차
            ['cat' => '자동차', 'title' => '중고차 구매 시 체크 포인트', 'content' => '처음 중고차를 구매하려고 합니다. 어떤 점들을 확인해야 하나요? 카팩스 확인 외에 다른 팁이 있나요?'],
            ['cat' => '자동차', 'title' => '차 보험 추천해 주세요', 'content' => '차 보험 갱신 시기인데 어느 회사가 제일 저렴한가요? 현재 월 $200 정도 내고 있습니다.'],
            ['cat' => '자동차', 'title' => '리스 만기 후 어떻게 하는 게 좋나요?', 'content' => '차 리스가 곧 끝나는데 바이아웃을 해야 할지 새 차로 바꿔야 할지 고민입니다.'],

            // 의료/보험
            ['cat' => '의료/보험', 'title' => '건강보험 없이 병원 가는 방법', 'content' => '현재 건강보험이 없는데 갑자기 아파서 병원에 가야 합니다. 보험 없이 갈 수 있는 방법이 있나요?'],
            ['cat' => '의료/보험', 'title' => 'PPO vs HMO 어떤 게 나은가요?', 'content' => '회사에서 건강보험을 선택해야 하는데 PPO와 HMO 중 어떤 게 좋을까요? 장단점을 알려주세요.'],
            ['cat' => '의료/보험', 'title' => '치과 보험 추천 부탁드립니다', 'content' => '치과 치료가 필요한데 좋은 치과 보험 추천해 주세요. 임플란트 커버 되는 보험이 있나요?'],

            // 교육
            ['cat' => '교육', 'title' => '미국 대학 입시 준비 타임라인', 'content' => '고등학생 자녀가 있는데 대학 입시 준비를 언제부터 어떻게 해야 하나요? SAT는 몇 학년부터?'],
            ['cat' => '교육', 'title' => '한글학교 vs 과외 어떤 게 좋을까요?', 'content' => '아이한테 한국어를 가르치고 싶은데 한글학교와 개인 과외 중 어떤 게 효과적인가요?'],
            ['cat' => '교육', 'title' => 'AP 과목 몇 개 정도 듣는 게 좋나요?', 'content' => '11학년 자녀가 AP 과목을 선택해야 하는데 몇 개 정도 듣는 게 적당한가요?'],

            // 취업
            ['cat' => '취업', 'title' => '미국에서 이직할 때 연봉 협상 팁', 'content' => '현재 직장에서 3년 일했고 이직을 고려하고 있습니다. 연봉 협상은 어떻게 하나요?'],
            ['cat' => '취업', 'title' => '한인 IT 회사에서 일하는 건 어떤가요?', 'content' => '한인이 운영하는 IT 회사에서 오퍼를 받았는데 한인 회사에서 일하는 건 어떤가요?'],
            ['cat' => '취업', 'title' => '영어 인터뷰 준비 방법', 'content' => '다음 주에 영어 인터뷰가 있는데 어떻게 준비하면 좋을까요? 특히 행동 면접(behavioral)이 걱정됩니다.'],

            // 생활정보
            ['cat' => '생활정보', 'title' => '미국에서 한국 택배 보내기 가장 싼 방법', 'content' => '한국에 택배를 보내려고 하는데 어떤 서비스가 제일 저렴하고 빠른가요?'],
            ['cat' => '생활정보', 'title' => '신용점수 빨리 올리는 방법', 'content' => '신용점수가 650인데 빨리 올리는 방법이 있나요? 집을 사고 싶은데 720은 되어야 한다고 해서요.'],
            ['cat' => '생활정보', 'title' => '미국에서 한국 드라마 볼 수 있는 서비스', 'content' => '넷플릭스 말고 한국 드라마를 볼 수 있는 스트리밍 서비스가 뭐가 있나요?'],

            // IT/기술
            ['cat' => 'IT/기술', 'title' => '아이폰 vs 안드로이드 추천해 주세요', 'content' => '새 폰을 사려는데 아이폰과 안드로이드 중 어떤 게 나을까요? 한국어 입력이 편한 걸로 추천해 주세요.'],
            ['cat' => 'IT/기술', 'title' => 'VPN 추천 부탁드립니다', 'content' => '한국 사이트 접속할 때 VPN이 필요한데 어떤 VPN이 좋나요? 무료/유료 다 괜찮습니다.'],
            ['cat' => 'IT/기술', 'title' => '프로그래밍 독학으로 취업 가능한가요?', 'content' => '비전공자인데 프로그래밍을 독학해서 IT 회사에 취업할 수 있나요? 어떤 언어부터 배워야 하나요?'],

            // 기타
            ['cat' => '기타', 'title' => '미국에서 반려동물 입양 절차', 'content' => '강아지를 입양하고 싶은데 미국에서 입양 절차가 어떻게 되나요? 셸터에서 입양하는 게 좋나요?'],
            ['cat' => '기타', 'title' => '한국 귀국 시 짐 보내기 방법', 'content' => '한국으로 이사하게 되었는데 짐을 어떻게 보내야 하나요? 비용과 시간이 궁금합니다.'],
            ['cat' => '기타', 'title' => '미국에서 한국 음식 재료 구하기', 'content' => '한국 마트가 없는 지역에 사는데 한국 음식 재료를 온라인으로 주문할 수 있는 곳이 있나요?'],
        ];

        $answerTemplates = [
            "저도 비슷한 경험이 있어서 답변 드립니다.\n\n{answer}\n\n도움이 되셨으면 좋겠습니다!",
            "{answer}\n\n제 경험을 바탕으로 말씀드린 거라 참고만 해주세요.",
            "안녕하세요, {answer}\n\n더 궁금한 점 있으시면 댓글 달아주세요.",
            "{answer}\n\n전문가 상담도 받아보시는 걸 추천드립니다.",
        ];

        $answerContents = [
            '제 경험상 보통 2~3개월 정도 걸렸습니다. 지역마다 차이가 있으니 해당 기관에 직접 문의하시는 게 가장 정확합니다.',
            '이 부분은 전문가의 도움을 받는 것이 좋습니다. 한인 변호사나 회계사를 추천드립니다. 초기 상담은 무료인 곳도 많아요.',
            '저도 처음엔 막막했는데 유튜브에서 관련 영상을 보고 많이 도움을 받았습니다. 요즘은 한국어로 된 자료도 많더라고요.',
            '이건 케이스 바이 케이스입니다. 본인의 상황에 따라 다르니 여러 군데 알아보시고 비교해 보세요.',
            '가장 중요한 건 서류를 미리 준비하는 겁니다. 필요한 서류 목록을 만들어서 하나씩 체크해 보세요.',
            '온라인에서 비슷한 질문을 검색해 보면 많은 정보가 나옵니다. Reddit의 한인 커뮤니티도 도움이 많이 됩니다.',
            '저는 지인 소개로 전문가를 만났는데 비용도 합리적이고 결과도 좋았습니다. 주변에 물어보시는 것도 방법입니다.',
            '이 문제는 시간이 좀 걸릴 수 있습니다. 인내심을 가지고 차근차근 진행하시면 됩니다. 화이팅!',
            '최근에 정책이 많이 바뀌어서 최신 정보를 확인하시는 게 중요합니다. 관련 정부 웹사이트를 꼭 체크해 보세요.',
            '개인적으로는 첫 번째 옵션을 추천합니다. 비용 대비 효과가 가장 좋았거든요.',
        ];

        $now  = now();
        $catNames = array_keys($categoryIds);

        for ($i = 0; $i < 300; $i++) {
            // Use prepared questions first, then repeat with variations
            if ($i < count($questions)) {
                $q = $questions[$i];
            } else {
                $q = $questions[$i % count($questions)];
                $q['title'] = $q['title'] . ' (추가질문 ' . intdiv($i, count($questions)) . ')';
            }

            $catId   = $categoryIds[$q['cat']] ?? $categoryIds[$catNames[array_rand($catNames)]];
            $hasBounty = rand(0, 100) > 70;
            $isResolved = rand(0, 100) > 50;
            $answerCount = rand(2, 5);

            $qaPost = QaPost::create([
                'user_id'       => $userIds[array_rand($userIds)],
                'category_id'   => $catId,
                'title'         => $q['title'],
                'content'       => $q['content'],
                'bounty_points' => $hasBounty ? rand(1, 10) * 10 : 0,
                'view_count'    => rand(10, 500),
                'answer_count'  => $answerCount,
                'is_resolved'   => $isResolved,
                'best_answer_id' => null,
                'created_at'    => $now->copy()->subDays(rand(0, 90))->subHours(rand(0, 23)),
                'updated_at'    => $now,
            ]);

            $bestAnswerId = null;
            for ($j = 0; $j < $answerCount; $j++) {
                $template = $answerTemplates[array_rand($answerTemplates)];
                $content  = str_replace('{answer}', $answerContents[array_rand($answerContents)], $template);

                $isBest = $isResolved && $j === 0;
                $answer = QaAnswer::create([
                    'qa_post_id' => $qaPost->id,
                    'user_id'    => $userIds[array_rand($userIds)],
                    'content'    => $content,
                    'like_count' => rand(0, 20),
                    'is_best'    => $isBest,
                    'created_at' => $qaPost->created_at->copy()->addHours(rand(1, 72)),
                    'updated_at' => $now,
                ]);

                if ($isBest) {
                    $bestAnswerId = $answer->id;
                }
            }

            if ($bestAnswerId) {
                $qaPost->update(['best_answer_id' => $bestAnswerId]);
            }
        }

        $this->command->info('QaSeeder: 300 QA posts with answers created');
    }
}
