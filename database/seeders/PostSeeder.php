<?php

namespace Database\Seeders;

use App\Models\Board;
use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Seeder;

class PostSeeder extends Seeder
{
    public function run(): void
    {
        $userIds  = User::pluck('id')->toArray();
        $boardIds = Board::pluck('id')->toArray();

        if (empty($userIds) || empty($boardIds)) {
            $this->command->warn('PostSeeder: users or boards missing, skipping.');
            return;
        }

        $titles = [
            '오늘 한인타운에서 있었던 일',
            'LA 한인 마트 세일 정보 공유합니다',
            '이민 생활 10년차, 느끼는 점들',
            '코스트코 추천 상품 리스트',
            '자녀 SAT 준비 어떻게 하시나요?',
            'H1B 비자 신청 경험 공유',
            '한인타운 맛집 추천해 주세요',
            '차 보험 어디가 제일 싼가요?',
            '영주권 인터뷰 후기',
            '미국에서 한국 음식 재료 구하기',
            '에어프라이어 추천 부탁드립니다',
            '출산 병원 추천 (LA 지역)',
            '미국에서 한국 드라마 보는 방법',
            '세금 보고 직접 하시나요? 회계사 맡기시나요?',
            '주말에 아이들과 가볼 만한 곳',
            '차 리스 vs 구매 어떤 게 나을까요?',
            '한국 귀국 시 면세 한도 질문',
            '동네 이웃과 소통하는 방법',
            '미국 생활 초보 팁 모음',
            '한인 교회/성당 추천해 주세요',
            '건강보험 선택 고민입니다',
            '아파트 렌트 팁 공유합니다',
            '직장 내 차별 경험 나누기',
            '한국 택배 보내기 제일 싼 곳',
            '아이 학교 입학 준비 체크리스트',
            '운전면허 갱신 방법 알려주세요',
            '이번 주말 날씨 너무 좋네요',
            '신용점수 올리는 방법',
            '블랙프라이데이 득템 후기',
            '한인 커뮤니티 행사 안내',
            '미국 의료비가 왜 이렇게 비싼지...',
            '추석 맞이 한인타운 행사',
            '401k 투자 어디에 하시나요?',
            '미국에서 김치 담그기 꿀팁',
            '새 아파트로 이사했습니다!',
            'USCIS 케이스 상태 확인법',
            '한인 변호사 추천 부탁합니다',
            '중고차 구매 시 주의사항',
            '아이비리그 입시 준비',
            '홈디포 세일 꿀템 정리',
            '코리안 BBQ 맛집 투어',
            '미국 시민권 시험 공부법',
            '한인 골프 모임 멤버 모집',
            '겨울 대비 히터 점검 팁',
            '한국 부모님 미국 초청 비자',
            '새해 목표 세우셨나요?',
            '주택 모기지 이자율 비교',
            '한인 식당 알바 구합니다',
            '트레이더조 추천 상품',
            '아이 한글 교육 어떻게 하시나요?',
        ];

        $contentTemplates = [
            "안녕하세요, 미국 생활 {years}년차입니다.\n\n{topic}에 대해 이야기해 볼까 합니다. 제 경험을 공유하면 다른 분들께도 도움이 될 것 같아서요.\n\n{detail}\n\n혹시 비슷한 경험이 있으시면 댓글로 공유해 주세요. 서로 도움이 되면 좋겠습니다.\n\n감사합니다!",
            "오늘 {location}에서 좋은 경험을 해서 글 올립니다.\n\n{topic} 관련해서 여러모로 알아보다가 좋은 정보를 얻었습니다.\n\n{detail}\n\n다른 분들도 참고하시면 좋을 것 같습니다. 질문 있으시면 댓글 달아주세요!",
            "{topic} 관련 질문드립니다.\n\n{detail}\n\n검색해 봤는데 정확한 답을 찾기가 어렵네요. 경험 있으신 분들의 조언 부탁드립니다.\n\n미리 감사합니다.",
            "안녕하세요! {topic} 정보 공유합니다.\n\n최근에 알게 된 유용한 정보인데요, 다른 분들도 알면 좋을 것 같아서 올립니다.\n\n{detail}\n\n도움이 되셨으면 좋겠습니다. 추가 질문은 댓글로 남겨주세요.",
            "{greeting}\n\n{topic}에 대해 고민이 많았는데 드디어 결정을 내렸습니다.\n\n{detail}\n\n비슷한 고민을 하시는 분들께 도움이 되길 바랍니다.\n\n좋은 하루 보내세요!",
        ];

        $topics = [
            '이민 생활', '세금 보고', '자녀 교육', '건강 보험', '부동산',
            '직장 생활', '한국 음식', '운전면허', '비자 관련', '투자',
            '인테리어', '영어 공부', '한인 커뮤니티', '여행 계획', '반려동물',
        ];

        $details = [
            "처음에는 정말 어려웠는데 시간이 지나면서 점점 나아지더라고요. 특히 주변 한인 분들의 도움이 많이 되었습니다. 같은 경험을 가진 사람들끼리 정보를 공유하면 훨씬 수월합니다.",
            "몇 달간 알아본 결과, 가격대도 합리적이고 서비스도 좋은 곳을 찾았습니다. 특히 한국어가 가능한 직원이 있어서 소통이 편했어요. 다른 분들도 한번 확인해 보시기 바랍니다.",
            "여러 군데 비교해 봤는데 결국은 후기가 제일 중요한 것 같습니다. 온라인 리뷰만 보지 마시고 직접 가서 확인해 보시는 걸 추천드립니다. 사진과 실제가 다른 경우가 많더라고요.",
            "주변에 같은 상황인 분들이 많더라고요. 다 같이 정보를 모으면 훨씬 좋은 결과를 얻을 수 있을 것 같습니다. 혹시 관심 있으시면 연락 주세요.",
            "인터넷에서 찾은 정보와 실제로 경험한 것이 좀 다른 부분이 있었습니다. 가능하면 최신 정보를 확인하시고, 전문가 상담을 받아보시는 것을 추천드립니다.",
            "가족들과 상의해서 결정했는데 결과적으로 아주 만족하고 있습니다. 처음에 걱정을 많이 했는데 생각보다 진행 과정이 수월했어요.",
            "미국에 오래 살다 보니 이제는 좀 익숙해졌지만, 처음 왔을 때는 정말 막막했습니다. 그때 이런 커뮤니티가 있었으면 좋았을 텐데... 지금이라도 후배님들을 위해 정보 남깁니다.",
            "여러 옵션을 비교한 결과를 정리해 봤습니다. 각자 상황이 다르니까 참고만 하시고 본인에게 맞는 것을 선택하시면 됩니다. 추가 질문은 댓글로 남겨주세요.",
        ];

        $greetings = ['안녕하세요!', '반갑습니다.', '좋은 하루입니다!', '안녕하세요, 회원 여러분!'];
        $locations  = ['한인타운', '코리아타운', '플러싱', '다운타운', '산타모니카', '시카고 북부', '아틀란타 북쪽', '달라스 캐롤턴 지역'];
        $years      = [2, 3, 5, 7, 10, 12, 15, 20];

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

        $now  = now();
        $rows = [];

        for ($i = 0; $i < 300; $i++) {
            $template = $contentTemplates[array_rand($contentTemplates)];
            $city     = $cities[array_rand($cities)];
            $hasLocation = rand(0, 100) > 40;

            $content = str_replace(
                ['{years}', '{topic}', '{detail}', '{location}', '{greeting}'],
                [
                    $years[array_rand($years)],
                    $topics[array_rand($topics)],
                    $details[array_rand($details)],
                    $locations[array_rand($locations)],
                    $greetings[array_rand($greetings)],
                ],
                $template
            );

            $rows[] = [
                'board_id'      => $boardIds[array_rand($boardIds)],
                'user_id'       => $userIds[array_rand($userIds)],
                'title'         => $titles[array_rand($titles)],
                'content'       => $content,
                'category'      => null,
                'images'        => null,
                'view_count'    => rand(10, 500),
                'like_count'    => rand(0, 50),
                'comment_count' => rand(0, 30),
                'is_pinned'     => $i < 5,
                'is_hidden'     => false,
                'lat'           => $hasLocation ? round($city['lat'] + rand(-200, 200) / 10000, 7) : null,
                'lng'           => $hasLocation ? round($city['lng'] + rand(-200, 200) / 10000, 7) : null,
                'city'          => $hasLocation ? $city['city'] : null,
                'state'         => $hasLocation ? $city['state'] : null,
                'zipcode'       => $hasLocation ? $city['zip'] : null,
                'created_at'    => $now->copy()->subDays(rand(0, 90))->subHours(rand(0, 23)),
                'updated_at'    => $now,
            ];
        }

        foreach (array_chunk($rows, 50) as $chunk) {
            Post::insert($chunk);
        }

        $this->command->info('PostSeeder: 300 posts created');
    }
}
