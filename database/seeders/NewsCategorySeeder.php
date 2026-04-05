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

        // Korean to romanized slug map for subcategories
        $subSlugs = [
            'H1B' => 'h1b', '영주권' => 'greencard', '시민권' => 'citizenship', 'DACA' => 'daca',
            '학생비자' => 'student-visa', '취업비자' => 'work-visa', '가족초청' => 'family-petition',
            '추방방어' => 'deportation-defense', '비자인터뷰' => 'visa-interview',
            '한인경제' => 'korean-economy', '부동산시장' => 'real-estate-market', '주식/투자' => 'stocks',
            '창업정보' => 'startup', '세금/회계' => 'tax', '은행/금융' => 'banking',
            '한미관계' => 'korea-us', '미국정치' => 'us-politics', '한국정치' => 'korea-politics',
            '선거' => 'election', '정책' => 'policy',
            '인종/차별' => 'race', '교육' => 'education', '의료/건강' => 'healthcare',
            '범죄/안전' => 'crime-safety', '환경' => 'environment',
            '자동차' => 'auto', '쇼핑/세일' => 'shopping', '음식/맛집' => 'food',
            '여행' => 'travel', '주거' => 'housing',
            'K-POP' => 'kpop', 'K-드라마' => 'kdrama', '영화' => 'movies',
            '공연/전시' => 'performance', '한류' => 'hallyu',
            'MLB' => 'mlb', 'NBA' => 'nba', 'NFL' => 'nfl', '축구' => 'soccer',
            '골프' => 'golf', '한국스포츠' => 'korea-sports',
            'IT뉴스' => 'it-news', '앱/서비스' => 'apps', 'AI' => 'ai',
            '스타트업' => 'startups', '가전' => 'electronics',
            '동포소식' => 'diaspora', '행사안내' => 'events', '봉사활동' => 'volunteer',
            '종교' => 'religion', '한인회' => 'korean-association',
        ];

        foreach ($categories as $name => $data) {
            $parent = NewsCategory::create([
                'name'      => $name,
                'slug'      => $data['slug'],
                'parent_id' => null,
            ]);
            $mainCount++;

            foreach ($data['subs'] as $idx => $sub) {
                $subSlug = $subSlugs[$sub] ?? $data['slug'] . '-sub-' . ($idx + 1);
                NewsCategory::create([
                    'name'      => $sub,
                    'slug'      => $data['slug'] . '-' . $subSlug,
                    'parent_id' => $parent->id,
                ]);
                $subCount++;
            }
        }

        $this->command->info("NewsCategorySeeder: {$mainCount} main + {$subCount} sub categories created");
    }
}
