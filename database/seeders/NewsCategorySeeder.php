<?php

namespace Database\Seeders;

use App\Models\NewsCategory;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;

class NewsCategorySeeder extends Seeder
{
    public function run(): void
    {
        $categories = [
            '이민/비자' => [
                'slug' => 'immigration',
                'subs' => ['H1B', '영주권', '시민권', 'DACA', '학생비자', '취업비자', '가족초청', '추방방어', '비자인터뷰'],
            ],
            '경제/비즈니스' => [
                'slug' => 'economy',
                'subs' => ['한인경제', '부동산시장', '주식/투자', '창업정보', '세금/회계', '은행/금융'],
            ],
            '정치' => [
                'slug' => 'politics',
                'subs' => ['한미관계', '미국정치', '한국정치', '선거', '정책'],
            ],
            '사회' => [
                'slug' => 'society',
                'subs' => ['인종/차별', '교육', '의료/건강', '범죄/안전', '환경'],
            ],
            '생활' => [
                'slug' => 'living',
                'subs' => ['자동차', '쇼핑/세일', '음식/맛집', '여행', '주거'],
            ],
            '문화/연예' => [
                'slug' => 'culture',
                'subs' => ['K-POP', 'K-드라마', '영화', '공연/전시', '한류'],
            ],
            '스포츠' => [
                'slug' => 'sports',
                'subs' => ['MLB', 'NBA', 'NFL', '축구', '골프', '한국스포츠'],
            ],
            '테크' => [
                'slug' => 'tech',
                'subs' => ['IT뉴스', '앱/서비스', 'AI', '스타트업', '가전'],
            ],
            '커뮤니티' => [
                'slug' => 'community',
                'subs' => ['동포소식', '행사안내', '봉사활동', '종교', '한인회'],
            ],
        ];

        $mainCount = 0;
        $subCount  = 0;

        foreach ($categories as $name => $data) {
            $parent = NewsCategory::create([
                'name'      => $name,
                'slug'      => $data['slug'],
                'parent_id' => null,
            ]);
            $mainCount++;

            foreach ($data['subs'] as $sub) {
                NewsCategory::create([
                    'name'      => $sub,
                    'slug'      => $data['slug'] . '-' . Str::slug($sub),
                    'parent_id' => $parent->id,
                ]);
                $subCount++;
            }
        }

        $this->command->info("NewsCategorySeeder: {$mainCount} main + {$subCount} sub categories created");
    }
}
