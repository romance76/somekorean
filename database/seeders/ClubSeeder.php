<?php

namespace Database\Seeders;

use App\Models\Club;
use App\Models\ClubMember;
use App\Models\User;
use Illuminate\Database\Seeder;

class ClubSeeder extends Seeder
{
    public function run(): void
    {
        $userIds = User::pluck('id')->toArray();
        if (empty($userIds)) { $this->command->warn('ClubSeeder: no users, skipping.'); return; }

        $clubs = [
            // 운동
            ['name' => 'LA 한인 골프 모임',         'category' => '운동', 'type' => 'local',  'desc' => 'LA 지역 한인 골프 동호회입니다. 매주 토요일 라운딩합니다.'],
            ['name' => '뉴욕 한인 러닝 클럽',       'category' => '운동', 'type' => 'local',  'desc' => '센트럴파크에서 매주 일요일 아침 러닝합니다.'],
            ['name' => '한인 테니스 동호회',         'category' => '운동', 'type' => 'local',  'desc' => '초보부터 고수까지 함께하는 테니스 모임입니다.'],
            ['name' => '한인 축구 클럽',             'category' => '운동', 'type' => 'local',  'desc' => '주말 축구 동호회입니다. 실력 무관!'],
            ['name' => '미국 한인 등산 모임',        'category' => '운동', 'type' => 'local',  'desc' => '매달 한 번 트레일 하이킹합니다.'],

            // 음악
            ['name' => '한인 밴드 동호회',           'category' => '음악', 'type' => 'local',  'desc' => '악기 연주를 좋아하시는 분들의 모임입니다.'],
            ['name' => 'K-POP 팬 클럽',              'category' => '음악', 'type' => 'online', 'desc' => 'K-POP 소식과 팬 활동을 함께 나눠요!'],
            ['name' => '한인 합창단',                'category' => '음악', 'type' => 'local',  'desc' => '한국 가곡과 팝송을 함께 부르는 합창 모임입니다.'],
            ['name' => '기타 동호회',                'category' => '음악', 'type' => 'local',  'desc' => '어쿠스틱 기타를 함께 배우고 연주합니다.'],
            ['name' => '트로트 사랑 모임',           'category' => '음악', 'type' => 'online', 'desc' => '트로트를 사랑하는 분들의 온라인 모임입니다.'],

            // 독서
            ['name' => '한인 북클럽',                'category' => '독서', 'type' => 'online', 'desc' => '매달 한 권의 책을 읽고 토론합니다.'],
            ['name' => '영어 원서 읽기 모임',        'category' => '독서', 'type' => 'online', 'desc' => '영어 원서를 함께 읽고 이야기 나눠요.'],
            ['name' => '한국 소설 독서 모임',        'category' => '독서', 'type' => 'online', 'desc' => '한국 작가의 소설을 매달 한 권씩 읽습니다.'],
            ['name' => '자기계발 독서 클럽',         'category' => '독서', 'type' => 'online', 'desc' => '자기계발서를 함께 읽고 성장해요.'],
            ['name' => '부모님을 위한 그림책 모임',  'category' => '독서', 'type' => 'online', 'desc' => '아이와 함께 읽을 그림책을 추천하는 모임입니다.'],

            // 요리
            ['name' => '한식 요리 동호회',           'category' => '요리', 'type' => 'online', 'desc' => '한식 레시피를 공유하고 함께 요리해요!'],
            ['name' => '베이킹 클럽',                'category' => '요리', 'type' => 'online', 'desc' => '빵, 케이크, 쿠키 등 베이킹을 함께 즐겨요.'],
            ['name' => '건강 식단 연구 모임',        'category' => '요리', 'type' => 'online', 'desc' => '건강한 식단과 레시피를 공유합니다.'],
            ['name' => '와인 & 치즈 클럽',           'category' => '요리', 'type' => 'local',  'desc' => '매달 와인 테이스팅 모임입니다.'],
            ['name' => '김치 담그기 모임',           'category' => '요리', 'type' => 'local',  'desc' => '시즌마다 함께 김치를 담급니다.'],

            // 여행
            ['name' => '미국 여행 동호회',           'category' => '여행', 'type' => 'online', 'desc' => '미국 곳곳의 여행지를 추천하고 후기를 나눠요.'],
            ['name' => '캠핑 & 아웃도어 클럽',       'category' => '여행', 'type' => 'local',  'desc' => '캠핑, 하이킹, 카약 등 아웃도어 활동을 함께해요.'],
            ['name' => '한국 여행 정보 모임',        'category' => '여행', 'type' => 'online', 'desc' => '한국 방문 시 유용한 정보를 공유합니다.'],
            ['name' => 'Road Trip 클럽',             'category' => '여행', 'type' => 'local',  'desc' => '같이 로드트립 떠나실 분 모집합니다!'],
            ['name' => '해외여행 정보 공유',         'category' => '여행', 'type' => 'online', 'desc' => '전 세계 여행 정보와 팁을 공유합니다.'],

            // 사진
            ['name' => '한인 사진 동호회',           'category' => '사진', 'type' => 'local',  'desc' => '사진 출사와 촬영 기법을 공유합니다.'],
            ['name' => '풍경 사진 클럽',             'category' => '사진', 'type' => 'online', 'desc' => '아름다운 풍경 사진을 공유하는 모임입니다.'],
            ['name' => '인물 사진 모임',             'category' => '사진', 'type' => 'local',  'desc' => '포트레이트 촬영을 함께 연습합니다.'],
            ['name' => '스마트폰 사진 클럽',         'category' => '사진', 'type' => 'online', 'desc' => '스마트폰으로 좋은 사진 찍는 법을 나눠요.'],

            // 게임
            ['name' => '한인 바둑 모임',             'category' => '게임', 'type' => 'online', 'desc' => '온라인으로 바둑을 두는 모임입니다.'],
            ['name' => '보드게임 클럽',              'category' => '게임', 'type' => 'local',  'desc' => '매주 모여서 보드게임을 즐깁니다.'],
            ['name' => 'PC 게임 동호회',             'category' => '게임', 'type' => 'online', 'desc' => '리그오브레전드, 발로란트 등 같이 하실 분!'],
            ['name' => '장기 동호회',                'category' => '게임', 'type' => 'online', 'desc' => '한국 전통 장기를 온라인으로 둡니다.'],
            ['name' => '마작 클럽',                  'category' => '게임', 'type' => 'local',  'desc' => '매주 금요일 저녁 마작 모임입니다.'],

            // 봉사
            ['name' => '한인 봉사 단체',             'category' => '봉사', 'type' => 'local',  'desc' => '지역사회를 위한 봉사활동을 함께합니다.'],
            ['name' => '노인 돌봄 봉사 모임',        'category' => '봉사', 'type' => 'local',  'desc' => '한인 어르신들을 위한 봉사 모임입니다.'],
            ['name' => '환경 보호 봉사단',           'category' => '봉사', 'type' => 'local',  'desc' => '비치 클린업, 재활용 캠페인 등 환경 봉사활동을 합니다.'],
            ['name' => '유학생 멘토링 봉사',         'category' => '봉사', 'type' => 'online', 'desc' => '새로 온 유학생들을 위한 멘토링 봉사입니다.'],
            ['name' => '푸드뱅크 봉사 모임',         'category' => '봉사', 'type' => 'local',  'desc' => '매달 푸드뱅크에서 봉사활동을 합니다.'],

            // 종교
            ['name' => '한인 성경 공부 모임',        'category' => '종교', 'type' => 'online', 'desc' => '매주 함께 성경을 읽고 나눕니다.'],
            ['name' => '한인 불교 명상 모임',        'category' => '종교', 'type' => 'local',  'desc' => '명상과 불교 수행을 함께하는 모임입니다.'],
            ['name' => '한인 천주교 교류 모임',      'category' => '종교', 'type' => 'local',  'desc' => '천주교 신자분들의 친목 모임입니다.'],

            // 기타
            ['name' => '한인 투자 스터디',           'category' => '기타', 'type' => 'online', 'desc' => '주식, 부동산, 암호화폐 등 투자 정보를 공유합니다.'],
            ['name' => '미국 생활 정보 모임',        'category' => '기타', 'type' => 'online', 'desc' => '미국 생활에 필요한 다양한 정보를 나눠요.'],
            ['name' => '한인 엄마 모임',             'category' => '기타', 'type' => 'local',  'desc' => '한인 엄마들의 육아 정보 교류 모임입니다.'],
            ['name' => '한인 창업자 네트워크',       'category' => '기타', 'type' => 'online', 'desc' => '창업 경험과 노하우를 나누는 모임입니다.'],
            ['name' => '영어 회화 스터디',           'category' => '기타', 'type' => 'online', 'desc' => '매주 영어 회화 연습을 함께합니다.'],
            ['name' => '한국어 가르치기 모임',       'category' => '기타', 'type' => 'online', 'desc' => '자녀에게 한국어를 가르치는 방법을 공유합니다.'],
            ['name' => '반려동물 사랑 모임',         'category' => '기타', 'type' => 'local',  'desc' => '반려동물과 함께하는 한인 모임입니다.'],
        ];

        $zips = ['90010', '11354', '60625', '30338', '75006', '77036', '98104', '94112', '22003', '19107'];

        $now = now();

        foreach ($clubs as $clubData) {
            $ownerId     = $userIds[array_rand($userIds)];
            $memberCount = rand(5, 80);

            $club = Club::create([
                'user_id'      => $ownerId,
                'name'         => $clubData['name'],
                'description'  => $clubData['desc'],
                'category'     => $clubData['category'],
                'image'        => null,
                'type'         => $clubData['type'],
                'zipcode'      => $clubData['type'] === 'local' ? $zips[array_rand($zips)] : null,
                'member_count' => $memberCount,
                'is_active'    => true,
                'created_at'   => $now->copy()->subDays(rand(10, 90)),
                'updated_at'   => $now,
            ]);

            // Add owner as admin member
            ClubMember::create([
                'club_id'   => $club->id,
                'user_id'   => $ownerId,
                'role'      => 'admin',
                'joined_at' => $club->created_at,
            ]);

            // Add random members (up to 10 for speed)
            $memberPool = array_diff($userIds, [$ownerId]);
            shuffle($memberPool);
            $membersToAdd = array_slice($memberPool, 0, min(10, $memberCount - 1));

            foreach ($membersToAdd as $memberId) {
                ClubMember::create([
                    'club_id'   => $club->id,
                    'user_id'   => $memberId,
                    'role'      => 'member',
                    'joined_at' => $now->copy()->subDays(rand(0, 60)),
                ]);
            }
        }

        $this->command->info('ClubSeeder: ' . count($clubs) . ' clubs created');
    }
}
