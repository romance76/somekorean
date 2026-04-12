<?php

namespace App\Console\Commands;

use App\Models\News;
use Illuminate\Console\Command;

/**
 * 제목 키워드 기반으로 뉴스 카테고리를 재분류한다.
 * FetchNews 가 모든 글을 "이민/비자" 로 떨궈놨던 문제를 바로잡음.
 */
class ReclassifyNews extends Command
{
    protected $signature = 'news:reclassify {--dry : preview only}';
    protected $description = 'Reclassify news into categories based on title keywords';

    // 카테고리 id 와 매칭 키워드. 위에서 아래로 우선순위 적용.
    private array $rules = [
        7 => [ // 스포츠
            '축구', '야구', '골프', '농구', '배구', '테니스', '손흥민', '메시', '호날두',
            '감독', 'MLS', '프리미어리그', 'K리그', '리그', '우승', '승리', '패배',
            '결승', '4강', '8강', 'KBO', '김하성', '이정후', '류현진', 'MLB', '올림픽',
            '월드컵', '컵', '토너먼트', '경기', '선수', '뮌헨', '레알', '바르사',
        ],
        6 => [ // 문화/연예
            '배우', '가수', '드라마', '영화', '별세', '앨범', '뮤직', '콘서트',
            '아이돌', '연예', 'BTS', '블랙핑크', '트와이스', 'TV', '방송', '예능',
            '뮤지컬', '공연', '전시', '갤러리', '미술', '오스카', '칸', '베를린',
            '해리우드', '넷플릭스', '디즈니', '스타', 'K팝', 'K-POP', '팝스타',
        ],
        2 => [ // 경제/비즈니스
            '주식', '환율', '증시', '부동산', '아파트', '집값', '기업', '투자',
            '매매', '부채', '금리', '인플레', '달러', '원화', '코스피', '나스닥',
            '다우', '실적', '매출', '영업이익', '반도체', '삼성', '현대', 'LG',
            'SK', '애플', '테슬라', '구글', '마이크로소프트', 'IPO', '상장',
            '경제', '세금', '보험', '연금', '펀드',
        ],
        3 => [ // 정치
            '대통령', '의원', '국회', '정부', '정당', '대선', '선거', '외교',
            '총리', '장관', '대통령실', '청와대', '민주당', '국민의힘',
            '윤석열', '이재명', '트럼프', '바이든', '해리스', '푸틴', '시진핑',
            '이란', '정상회담', '협상', '정책', '법안', '입법',
        ],
        4 => [ // 사회
            '사고', '화재', '범죄', '경찰', '구속', '체포', '살인', '사망',
            '실종', '교통', '추돌', '충돌', '사망자', '부상', '피해', '재난',
            '지진', '홍수', '태풍', '폭설', '사건',
        ],
        8 => [ // 테크
            'AI', '인공지능', 'ChatGPT', 'GPT', '로봇', '자동차', '전기차', 'EV',
            '테슬라', '배터리', '반도체', '클라우드', '앱', '스마트폰', '아이폰',
            '갤럭시', '소프트웨어', '개발', '프로그래밍', '해킹', '사이버', '보안',
            '메타버스', 'VR', 'AR', '드론', '우주', '위성', '로켓', 'SpaceX',
        ],
        5 => [ // 생활
            '건강', '의료', '병원', '의사', '진료', '치료', '다이어트', '음식',
            '레시피', '요리', '맛집', '여행', '호텔', '항공', '관광', '카페',
            '레스토랑', '봄', '여름', '가을', '겨울', '날씨', '기온',
        ],
        1 => [ // 이민/비자
            '이민', '비자', '영주권', '시민권', '한인', '그린카드', 'DACA',
            'I-485', 'I-130', 'H-1B', 'OPT', 'USCIS', '추방', '불법체류',
            '귀화', '난민',
        ],
    ];

    public function handle(): int
    {
        $dry = $this->option('dry');
        $this->info('Reclassifying news by title keywords...');

        $changed = [];
        $matched = 0;
        $total = 0;

        News::chunkById(100, function ($rows) use (&$changed, &$matched, &$total, $dry) {
            foreach ($rows as $n) {
                $total++;
                $title = $n->title ?? '';
                $newCat = $this->matchCategory($title);
                if ($newCat === null) continue;
                if ($newCat === $n->category_id) { $matched++; continue; }
                $changed[$newCat] = ($changed[$newCat] ?? 0) + 1;
                if (!$dry) {
                    $n->category_id = $newCat;
                    $n->save();
                }
                $matched++;
            }
        });

        $this->info("total=$total matched=$matched");
        $catNames = \App\Models\NewsCategory::pluck('name', 'id');
        foreach ($changed as $cid => $c) {
            $this->line("  → {$catNames[$cid]}: $c");
        }
        if ($dry) $this->warn('DRY RUN - no changes written');
        return 0;
    }

    private function matchCategory(string $title): ?int
    {
        foreach ($this->rules as $cid => $keywords) {
            foreach ($keywords as $kw) {
                if (mb_stripos($title, $kw) !== false) return $cid;
            }
        }
        return null;
    }
}
