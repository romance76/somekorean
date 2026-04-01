<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ImmigrationNewsSeeder extends Seeder
{
    public function run(): void
    {
        $yesterday = Carbon::yesterday();
        $twoDaysAgo = Carbon::now()->subDays(2);

        $articles = [
            // 이민/비자
            [
                'title'        => 'H-1B 비자 2026년 신청 기간 및 주요 변경사항 총정리',
                'summary'      => 'USCIS가 2026 회계연도 H-1B 비자 신청 관련 새로운 지침을 발표했습니다. 전자 등록 절차와 추첨 방식이 변경되어 한인 전문직 종사자들의 주의가 필요합니다.',
                'content'      => "미국 시민권 및 이민국(USCIS)이 H-1B 비자 신청과 관련한 2026년 새로운 절차를 발표했다.\n\n올해부터 H-1B 비자 신청자는 myUSCIS 계정을 통해 전자 등록을 완료해야 하며, 추첨 방식으로 청원서 제출 자격이 부여된다. 등록 기간은 보통 3월 첫째 주부터 시작된다.\n\nH-1B 비자는 전문직 종사자를 위한 비이민 비자로, IT, 의학, 법률, 회계 등 특수 분야의 외국인 근로자들이 미국에서 합법적으로 근무할 수 있도록 허가한다.\n\n특히 한인 IT 전문직 종사자들의 관심이 집중되고 있으며, 이민 변호사들은 가급적 일찍 준비할 것을 권고하고 있다. 추첨 당첨 후 청원서 제출까지의 절차와 비용도 꼼꼼히 확인해야 한다.",
                'url'          => 'https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations',
                'source'       => 'USCIS',
                'category'     => '이민/비자',
                'published_at' => $yesterday,
            ],
            [
                'title'        => '영주권 신청 I-485 처리 기간 12개월로 단축 — 한인들 주목',
                'summary'      => '이민국이 영주권 신청서(I-485) 처리 기간을 평균 18개월에서 12개월로 단축한다고 발표. 취업 기반 및 가족 초청 영주권 신청자 모두 해당됩니다.',
                'content'      => "미국 이민국(USCIS)이 영주권 신청서인 I-485 처리 기간을 대폭 단축하겠다고 발표했다.\n\n이민국에 따르면 현재 평균 18개월이 걸리던 처리 기간이 새로운 업무 효율화 시스템 도입으로 12개월 이내로 단축될 예정이다.\n\n이번 조치는 취업 기반 영주권(EB-2, EB-3) 신청자들과 가족 초청 영주권 신청자들에게 큰 혜택이 될 것으로 보인다.\n\n현재 영주권을 신청 중인 한인들은 이민 변호사와 상담하여 자신의 케이스가 이번 정책 변화에 어떤 영향을 받는지 확인할 것을 권고한다.",
                'url'          => 'https://www.uscis.gov/green-card/green-card-processes-and-procedures/adjustment-of-status',
                'source'       => 'USCIS',
                'category'     => '이민/비자',
                'published_at' => $yesterday,
            ],
            [
                'title'        => 'DACA 프로그램 최신 현황: 연방 법원 판결과 한인 드리머들',
                'summary'      => '연방 법원의 DACA 관련 최신 판결로 약 60만 명의 드리머에 영향 예상. 한인 커뮤니티 이민 변호사 조언 필수.',
                'content'      => "DACA(불법체류 청소년 추방 유예) 프로그램 관련 연방 법원의 최신 판결이 나왔다.\n\n법원은 기존 DACA 수혜자들에 대한 즉각적인 추방 조치는 취하지 않기로 했다. 현재 DACA 혜택을 받고 있는 약 60만 명의 드리머 중 한국계 미국인도 상당수 포함되어 있어 한인 커뮤니티의 우려가 크다.\n\n이민 법률 전문가들은 DACA 수혜자들이 가능한 한 빨리 이민 변호사와 상담하여 영주권이나 다른 합법적 신분 취득 방법을 모색할 것을 강력히 권고하고 있다.\n\nDREAM Act 입법화 움직임도 계속되고 있어 향후 추이를 주시할 필요가 있다.",
                'url'          => 'https://www.uscis.gov/DACA',
                'source'       => 'USCIS',
                'category'     => '이민/비자',
                'published_at' => $yesterday,
            ],
            // 미국생활
            [
                'title'        => '미국 세금 신고 시즌: 한인들이 놓치기 쉬운 절세 항목 7가지',
                'summary'      => '4월 15일 세금 신고 마감을 앞두고 한인 이민자들이 자주 놓치는 공제 항목과 절세 방법을 정리했습니다. FBAR 신고 의무도 확인하세요.',
                'content'      => "미국 연방 세금 신고 마감일(4월 15일)이 다가오면서 한인 커뮤니티의 관심이 높아지고 있다.\n\n한인 이민자들이 자주 놓치는 공제 항목으로는 ①해외 소득 면제(FEIE), ②주택 담보 대출 이자 공제, ③교육 관련 공제, ④의료비 공제, ⑤자선 기부 공제 등이 있다.\n\n특히 한국에 소득이 있는 한인의 경우 FBAR 및 FATCA 신고 의무가 있으며, 이를 위반할 경우 최대 수만 달러의 벌금이 부과될 수 있다.\n\n공인 회계사(CPA)나 세무사와 상담하여 최대한의 환급을 받고 법적 문제를 예방할 것을 권고한다.",
                'url'          => 'https://www.koreadaily.com/tax-guide-2026',
                'source'       => '미주중앙일보',
                'category'     => '미국생활',
                'published_at' => $yesterday,
            ],
            [
                'title'        => '미국 건강보험 오픈 인롤먼트 기간 — 한인들을 위한 완전 가이드',
                'summary'      => '건강보험 선택 시 한인 가정이 고려해야 할 HMO vs PPO 차이, 코리안 의사 네트워크, 정부 보조금 신청 방법을 정리했습니다.',
                'content'      => "미국에 사는 한인들에게 건강보험 선택은 중요한 연간 과제다.\n\nHMO(건강유지기구)는 주치의를 통한 의뢰가 필요하고 비용이 낮은 반면, PPO(우선 공급자 기관)는 의뢰 없이 전문의 방문이 가능해 유연성이 높다.\n\nACA(오바마케어) 마켓플레이스를 통해 건강보험을 구매하면 소득에 따른 정부 보조금(Premium Tax Credit)을 받을 수 있다.\n\n한인 의사와 소통이 중요한 경우 Korean-speaking provider가 네트워크에 포함된 플랜을 선택하는 것이 중요하다. H마트, 코리아타운 인근 지역에는 한국어 가능 의사들이 많이 분포해 있다.",
                'url'          => 'https://www.koreatimes.com/health-insurance-guide',
                'source'       => '미주한국일보',
                'category'     => '미국생활',
                'published_at' => $yesterday,
            ],
            // 경제 (미국/한인 관련)
            [
                'title'        => '트럼프 관세 정책으로 한국산 제품 가격 인상 우려 — 미주 한인 소비자 영향은?',
                'summary'      => '미국의 추가 관세 부과 조치로 한국산 전자제품, 자동차, 식품 가격 인상 가능성. 한인 마트와 가전제품 구매 계획에 영향 전망.',
                'content'      => "트럼프 행정부의 추가 관세 정책이 한국산 제품에 미치는 영향에 대한 우려가 커지고 있다.\n\n전자제품, 자동차, 철강 등 주요 한국 수출품에 대한 관세가 인상될 경우 미국 내 한국 제품 가격도 오를 가능성이 높다.\n\n특히 한인 마트에서 판매되는 한국산 식품과 일상용품들의 가격 인상이 예상되어 한인 소비자들의 부담이 늘어날 전망이다.\n\n한인 사업체들도 원가 상승에 대비한 경영 전략을 마련해야 할 것으로 보인다.",
                'url'          => 'https://www.koreaherald.com/tariff-impact-korean-americans',
                'source'       => '코리아헤럴드',
                'category'     => '경제',
                'published_at' => $yesterday,
            ],
        ];

        $inserted = 0;
        foreach ($articles as $article) {
            $exists = DB::table('news')->where('url', $article['url'])->exists();
            if (!$exists) {
                DB::table('news')->insert(array_merge($article, [
                    'created_at' => now(),
                    'updated_at' => now(),
                ]));
                $inserted++;
            }
        }

        $this->command->info("이민/비자 뉴스 {$inserted}건 추가 완료");
    }
}
