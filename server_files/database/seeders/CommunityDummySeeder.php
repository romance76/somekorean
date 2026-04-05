<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class CommunityDummySeeder extends Seeder
{
    public function run(): void
    {
        $userIds = DB::table('users')->pluck('id')->toArray();
        if (empty($userIds)) {
            $this->command->error('users 테이블에 데이터가 없습니다. FakeUsersSeeder를 먼저 실행하세요.');
            return;
        }

        $boardIds = DB::table('boards')->where('is_active', true)->pluck('id')->toArray();
        if (empty($boardIds)) {
            // boards 가 비어있으면 기본 게시판 생성
            $defaultBoards = [
                ['name' => '자유게시판', 'slug' => 'free', 'category' => 'community', 'description' => '자유롭게 이야기해요', 'icon' => null, 'sort_order' => 1, 'is_active' => true, 'created_at' => now(), 'updated_at' => now()],
                ['name' => '정보게시판', 'slug' => 'info', 'category' => 'community', 'description' => '유용한 정보를 공유해요', 'icon' => null, 'sort_order' => 2, 'is_active' => true, 'created_at' => now(), 'updated_at' => now()],
                ['name' => '유머게시판', 'slug' => 'humor', 'category' => 'community', 'description' => '웃긴 이야기 모음', 'icon' => null, 'sort_order' => 3, 'is_active' => true, 'created_at' => now(), 'updated_at' => now()],
                ['name' => '질문게시판', 'slug' => 'question', 'category' => 'community', 'description' => '궁금한 점을 질문하세요', 'icon' => null, 'sort_order' => 4, 'is_active' => true, 'created_at' => now(), 'updated_at' => now()],
                ['name' => '맛집게시판', 'slug' => 'food', 'category' => 'community', 'description' => '맛집 정보를 나눠요', 'icon' => null, 'sort_order' => 5, 'is_active' => true, 'created_at' => now(), 'updated_at' => now()],
                ['name' => '이민생활', 'slug' => 'immigrant', 'category' => 'community', 'description' => '이민 생활 이야기', 'icon' => null, 'sort_order' => 6, 'is_active' => true, 'created_at' => now(), 'updated_at' => now()],
            ];
            DB::table('boards')->insert($defaultBoards);
            $boardIds = DB::table('boards')->where('is_active', true)->pluck('id')->toArray();
        }

        $this->command->info('커뮤니티 게시물 300개 생성 중...');

        // ── 제목 풀 (다양한 카테고리별) ──
        $titles = [
            // 일상/자유
            'LA 한인타운 새로 생긴 카페 추천', '미국 이민 10년차 느낀점', '오늘 날씨 진짜 좋네요',
            '주말에 뭐하세요?', '오늘 하루도 수고했어요', '미국 생활 소소한 행복',
            '한국이 그리울 때', '이번 주 금요일 번개 모실 분?', '오늘 기분 좋은 일이 있었어요',
            '미국에서 한국인으로 살아가기', '퇴근 후 취미생활 뭐하세요?', '오늘 저녁 뭐 먹을까요',
            '주말 계획 세우기', '미국 일상 브이로그 찍어볼까', '혼밥 하시는 분들 모여라',
            '오늘도 야근이에요...', '비 오는 날 생각나는 한국 음식', '이사한 지 한 달 후기',
            '소소하지만 확실한 행복', '아침에 일어나기 힘든 분 손!', '집에서 할 수 있는 운동 추천',
            '넷플릭스 한국 드라마 추천', '한인 동네 카풀 같이 하실 분', '오늘 본 재밌는 영상',
            '미국 운전 적응기 ㅋㅋ', '여름에 갈만한 곳 추천', '캘리포니아 날씨 최고',
            '크리스마스 계획 있으세요?', '새해 목표 공유해요', '감사한 하루',
            // 정보/이민
            'SSN 분실 시 재발급 방법', 'EAD 카드 갱신 소요기간', '영주권 인터뷰 후기',
            'H1B 비자 추첨 결과 공유', '시민권 시험 공부 팁', 'F1 비자 OPT 신청 방법',
            'I-140 승인 후 다음 단계', 'USCIS 케이스 상태 확인법', '이민 변호사 추천해주세요',
            '여행허가서(AP) 신청 후기', '미국 여권 갱신 절차', '한국 영사관 방문 후기',
            '재외국민등록 하는 방법', '이중국적 관련 질문', '한국 운전면허 교환 방법',
            // 맛집/음식
            '코리아타운 맛집 TOP 5', '뉴저지 한식당 새로 오픈', '코스트코 추천 식품 리스트',
            'H마트 세일 정보 공유', '집에서 만든 떡볶이 대박', '미국에서 먹는 한국 라면',
            '트레이더조 추천 아이템', '한인마트 vs 미국마트 비교', '에어프라이어 레시피 공유',
            '냉장고에 있는 것으로 요리하기', '오늘 해먹은 요리 자랑', '식재료 싸게 사는 팁',
            'Yelp 별점 5점 한식당', '미국에서 배달음식 어떻게 시켜요?', '홀푸드 할인 꿀팁',
            // 유머
            '미국 살면서 겪은 문화충격 ㅋㅋ', '영어 실수담 모음 ㅋㅋㅋ', '한국 사람만 아는 공감',
            '미국인 남편이 김치 먹은 반응', '치킨이 먹고싶은 새벽 3시', '미국 운전 중 당황했던 순간',
            '한국 과자 먹고 놀란 미국인', '발음 때문에 생긴 해프닝', '미국 마트에서 생긴 일',
            '처음 팁 줄 때 당황했던 기억', 'Costco 가서 카트 한가득', '할로윈에 한복 입고 나감',
            // 질문
            '세금보고 어디서 하세요?', '차 보험 어디가 저렴한가요?', '아파트 렌트 계약 시 주의점',
            '미국 통장 추천해주세요', '핸드폰 요금제 추천', '인터넷 서비스 어디가 좋아요?',
            '건강보험 가입 방법', '미국 대학원 추천', '유아 교육 프로그램 정보',
            '자동차 리스 vs 구매', '집 수리 업체 추천', '가을 여행지 추천해주세요',
            '크레딧 점수 올리는 법', '미국에서 한국 책 주문 방법', '한인 치과 추천',
            // 이민생활
            '미국 생활 적응 힘드신 분', '한국에 언제 갈 수 있을까', '이민 와서 처음 1년 회고',
            '미국에서 외로움 극복하기', '한인 커뮤니티의 장단점', '미국 직장 문화 적응기',
            '아이 이중언어 교육 방법', '한국 부모님 방문 비자', '미국 은퇴 준비 어떻게',
            '소규모 비즈니스 시작하기', '미국에서 부업 추천', '재택근무 꿀팁 공유',
            '미국 주택 구매 과정', '이웃과 좋은 관계 유지법', '미국 공립학교 입학 절차',
            // 기타
            '오늘의 TMI', '심심한데 대화 나눠요', '이번 달 목표 공유', '좋은 글 공유합니다',
            '감동받은 이야기', '추천하는 유튜브 채널', '이번 주 좋은 일', '생일인데 축하해주세요',
            '반려동물 자랑 타임', '운동 같이 하실 분', '독서 모임 참여하실 분',
            '한국 뉴스 보다가 생각난 것', '미국에서 한국 TV 보는 법', '가을 단풍 명소 추천',
        ];

        // ── 내용 템플릿 풀 ──
        $contentTemplates = [
            "안녕하세요, {region}에서 생활하고 있는 한인입니다. {topic}에 대해서 이야기해볼까 해요.\n\n솔직히 미국 생활이 쉽진 않지만, 이런 커뮤니티가 있어서 큰 힘이 되네요. 같은 경험 있으신 분들 댓글로 이야기 나눠요!",
            "여러분 혹시 {topic} 관련해서 좋은 정보 있으시면 공유해주세요.\n\n저는 {region} 쪽에 살고 있는데요, 주변에 한인분들이 많지 않아서 온라인으로 정보 모으고 있어요. 다들 어떻게 하시는지 궁금합니다.",
            "{topic}에 대해 제 경험을 나눠볼게요.\n\n미국에 온 지 {years}년 정도 됐는데, 처음엔 정말 막막했어요. 지금은 많이 적응했지만 아직도 새로운 것들이 많네요. 특히 {region} 지역은 한인분들이 많아서 좋은 것 같아요.",
            "오늘 {topic} 때문에 하루종일 고민했어요.\n\n같은 고민 있으신 분? 혼자 끙끙 앓지 말고 같이 이야기해봐요. 미국 생활 선배님들의 조언이 절실합니다!",
            "{region}에서 {topic} 관련 꿀팁을 알게 돼서 공유해요.\n\n미국 생활하면서 이런 정보는 정말 금같은 것 같아요. 혹시 더 좋은 방법 아시는 분 있으시면 댓글 부탁드려요!",
            "안녕하세요! {region} 거주중입니다.\n\n{topic}을 주제로 이야기 나누고 싶어서 글 올립니다. 미국 한인 커뮤니티에서 서로 도움 주고받으면 좋겠어요. 저도 아는 거 있으면 최대한 답변해드릴게요.",
            "미국 생활 {years}년차인데 {topic} 때문에 글을 쓰게 됐어요.\n\n이민 초기에는 몰랐는데 시간이 지나니까 이런 것들이 중요하더라고요. 경험담이나 조언 부탁드려요.",
            "{topic}! 저만 이런 생각 하는 건 아니겠죠?\n\n미국에서 살면서 느끼는 크고 작은 것들... 같은 생각 하시는 분들이 있으면 좋겠어요. {region} 지역 분들 특히 환영합니다!",
            "{region}에서 {topic} 경험해보신 분 계세요?\n\n주변에 물어볼 사람이 없어서 여기에 올립니다. 비슷한 경험 있으시면 어떻게 해결하셨는지 알려주시면 감사하겠습니다.",
            "오랜만에 글 올려요. {topic}에 대한 솔직한 생각을 적어봅니다.\n\n미국 한인으로서 느끼는 감정들, 공감하시는 분들이 많을 것 같아요. {region}에서 보내는 일상이 때론 외롭지만, 이 커뮤니티 덕분에 힘을 얻고 있어요.",
        ];

        $regions = ['LA', 'New York', 'Atlanta', 'Chicago', 'Seattle', 'Dallas', 'Houston', 'San Francisco', 'Boston', 'Miami', 'San Jose', 'Virginia', 'New Jersey', 'Denver', 'Portland'];
        $topics = [
            '이민 생활', '영어 공부', '자녀 교육', '맛집 정보', '건강 관리',
            '직장 생활', '부동산', '세금 보고', '비자 문제', '문화 적응',
            '한식 요리', '운전 면허', '보험 가입', '투자', '은퇴 준비',
            '이사 계획', '학교 입학', '건강보험', '차량 구매', '주말 활동',
        ];

        $now = Carbon::now();
        $postRows = [];

        for ($i = 0; $i < 300; $i++) {
            $title = $titles[$i % count($titles)];
            $region = $regions[array_rand($regions)];
            $topic = $topics[array_rand($topics)];
            $years = rand(1, 15);
            $template = $contentTemplates[array_rand($contentTemplates)];

            $content = str_replace(
                ['{region}', '{topic}', '{years}'],
                [$region, $topic, (string)$years],
                $template
            );

            // 가끔 이모지 추가
            $emojis = ['', '', ' ^^', ' ㅎㅎ', '', '', '', ''];
            $content .= $emojis[array_rand($emojis)];

            // 미국 시간대 7am~11pm
            $daysAgo = rand(0, 90);
            $hour = rand(7, 23);
            $minute = rand(0, 59);
            $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute($minute)->setSecond(rand(0, 59));

            $postRows[] = [
                'board_id'      => $boardIds[array_rand($boardIds)],
                'user_id'       => $userIds[array_rand($userIds)],
                'title'         => $title,
                'content'       => $content,
                'thumbnail'     => null,
                'images'        => null,
                'view_count'    => rand(50, 3000),
                'like_count'    => rand(0, 80),
                'comment_count' => 0, // 나중에 업데이트
                'is_pinned'     => false,
                'is_notice'     => false,
                'is_anonymous'  => rand(0, 100) < 5, // 5% 익명
                'status'        => 'active',
                'created_at'    => $createdAt,
                'updated_at'    => $createdAt,
            ];
        }

        // 50개씩 chunk insert
        foreach (array_chunk($postRows, 50) as $chunk) {
            DB::table('posts')->insert($chunk);
        }
        $this->command->info('게시물 300개 생성 완료.');

        // ── 댓글 1,500개 ──
        $this->command->info('댓글 1,500개 생성 중...');

        $postIds = DB::table('posts')->orderByDesc('id')->limit(300)->pluck('id')->toArray();
        if (empty($postIds)) {
            $this->command->error('게시물이 없습니다.');
            return;
        }

        $commentTexts = [
            '좋은 정보 감사합니다!', '저도 같은 경험 있어요 ㅎㅎ', '공감이요~',
            '이거 몰랐는데 알려주셔서 감사합니다', '와 대박이네요', '참고하겠습니다!',
            '저도 궁금했던 내용이에요', '정리해주셔서 감사합니다', '도움이 많이 됐어요',
            '저는 좀 다른 경험을 했는데요...', '이 부분 좀 더 자세히 알 수 있을까요?',
            '맞아요 맞아요 ㅋㅋ', '완전 공감합니다', '이런 글이 더 많았으면 좋겠어요',
            '감사합니다! 바로 해봐야겠어요', 'ㅋㅋㅋ 저만 그런게 아니었군요',
            '좋은 글 감사해요', '오 이거 꿀팁이네요!', '저도 비슷한 상황이에요',
            '화이팅입니다!', '덕분에 큰 도움 됐어요', '이 정보 찾고 있었는데!',
            '추가 질문 있는데 괜찮을까요?', '저도 경험담 하나 남길게요',
            '진짜 맞는 말씀이에요', '생각해볼 부분이네요', '새로운 관점이에요',
            '오 저도 해봐야겠어요', '감사합니다 북마크했어요', 'ㅋㅋ 재밌네요',
            '좋은 하루 되세요!', '다음에 또 좋은 글 부탁드려요', '구독하고 갑니다',
            '저랑 상황이 비슷하네요', '유용한 정보 감사합니다', '덕분에 힘을 얻었어요',
            '맞아요 미국 생활 쉽지 않죠', '같이 힘내봐요!', '좋은 경험 공유 감사해요',
            '한인 커뮤니티 짱!', '이런 커뮤니티가 있어서 다행이에요', '서로 도와가며 살아요',
            '댓글 보니까 다들 비슷한 고민이시네요', '여기서 많이 배워가요',
            '저도 LA인데 같이 해요!', '뉴욕에서도 비슷한 경험 했어요',
            '시카고는 좀 다를 수 있어요', '텍사스도 같은 상황이에요',
            '아 그렇군요! 감사합니다', '오늘도 좋은 글 읽고 갑니다',
            '핵공감 ㅋㅋㅋ', '진심 도움됩니다', '소중한 정보네요',
            '저도 알려드릴게요!', '좋은 커뮤니티 감사합니다', '다음에 만나요!',
        ];

        $commentRows = [];
        $postCommentCounts = [];

        $totalComments = 0;
        foreach ($postIds as $postId) {
            $numComments = rand(2, 8);
            $postCommentCounts[$postId] = $numComments;
            $totalComments += $numComments;
        }

        // 1500개에 맞추기 위해 조정
        while ($totalComments < 1500) {
            $randomPost = $postIds[array_rand($postIds)];
            $postCommentCounts[$randomPost]++;
            $totalComments++;
        }
        while ($totalComments > 1500) {
            $randomPost = $postIds[array_rand($postIds)];
            if ($postCommentCounts[$randomPost] > 2) {
                $postCommentCounts[$randomPost]--;
                $totalComments--;
            }
        }

        foreach ($postCommentCounts as $postId => $numComments) {
            $postUserId = DB::table('posts')->where('id', $postId)->value('user_id');
            $otherUsers = array_values(array_filter($userIds, fn($uid) => $uid !== $postUserId));
            if (empty($otherUsers)) $otherUsers = $userIds;

            for ($c = 0; $c < $numComments; $c++) {
                $daysAgo = rand(0, 85);
                $hour = rand(7, 23);
                $createdAt = $now->copy()->subDays($daysAgo)->setHour($hour)->setMinute(rand(0, 59))->setSecond(rand(0, 59));

                $commentRows[] = [
                    'post_id'    => $postId,
                    'user_id'    => $otherUsers[array_rand($otherUsers)],
                    'parent_id'  => null,
                    'content'    => $commentTexts[array_rand($commentTexts)],
                    'like_count' => rand(0, 15),
                    'is_anonymous' => false,
                    'status'     => 'active',
                    'created_at' => $createdAt,
                    'updated_at' => $createdAt,
                ];
            }
        }

        // 50개씩 chunk insert
        foreach (array_chunk($commentRows, 50) as $chunk) {
            DB::table('comments')->insert($chunk);
        }

        // comment_count 업데이트
        foreach ($postCommentCounts as $postId => $count) {
            DB::table('posts')->where('id', $postId)->update(['comment_count' => $count]);
        }

        $this->command->info('댓글 ' . count($commentRows) . '개 생성 완료.');
        $this->command->info('CommunityDummySeeder 완료!');
    }
}
