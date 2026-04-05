<?php

namespace Database\Seeders;

use App\Models\Board;
use Illuminate\Database\Seeder;

class BoardSeeder extends Seeder
{
    public function run(): void
    {
        $boards = [
            ['name' => '자유게시판',   'slug' => 'free',        'description' => '자유롭게 이야기를 나눠보세요'],
            ['name' => '정보공유',     'slug' => 'info',        'description' => '유용한 정보를 공유하는 공간입니다'],
            ['name' => '생활꿀팁',     'slug' => 'tips',        'description' => '미국 생활에 도움되는 꿀팁 모음'],
            ['name' => '맛집후기',     'slug' => 'food',        'description' => '맛집 후기와 추천을 나누세요'],
            ['name' => '여행이야기',   'slug' => 'travel',      'description' => '여행 경험과 추천 장소를 공유해요'],
            ['name' => '자녀교육',     'slug' => 'education',   'description' => '자녀 교육 정보와 경험을 나눠요'],
            ['name' => '이민생활',     'slug' => 'immigration', 'description' => '이민 생활의 모든 것을 이야기해요'],
            ['name' => '건강정보',     'slug' => 'health',      'description' => '건강 관련 정보와 팁을 공유합니다'],
            ['name' => '유머',         'slug' => 'humor',       'description' => '웃긴 이야기, 짤, 유머 모음'],
            ['name' => '고민상담',     'slug' => 'advice',      'description' => '고민을 나누고 조언을 구해보세요'],
            ['name' => '홍보/광고',    'slug' => 'promotion',   'description' => '업소 홍보 및 광고 게시판'],
        ];

        foreach ($boards as $i => $board) {
            Board::create(array_merge($board, [
                'sort_order' => ($i + 1) * 10,
                'is_active'  => true,
            ]));
        }

        $this->command->info('BoardSeeder: ' . count($boards) . ' boards created');
    }
}
