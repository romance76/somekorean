<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\NewsCategory;

class NewsCategorySeeder extends Seeder
{
    public function run(): void
    {
        NewsCategory::truncate();

        $mainCategories = [
            ['name' => '사회',       'name_en' => 'Society',          'slug' => 'society',       'icon' => '🏛️', 'color' => '#e0e7ff', 'priority' => 1],
            ['name' => '경제',       'name_en' => 'Economy',          'slug' => 'economy',       'icon' => '💰', 'color' => '#dcfce7', 'priority' => 2],
            ['name' => '라이프',     'name_en' => 'Life',             'slug' => 'life',           'icon' => '🌿', 'color' => '#fef9c3', 'priority' => 3],
            ['name' => '연예/스포츠','name_en' => 'Entertainment',    'slug' => 'entertainment', 'icon' => '⭐', 'color' => '#fce7f3', 'priority' => 4],
            ['name' => 'ASK미국',    'name_en' => 'Ask America',      'slug' => 'ask-america',   'icon' => '🇺🇸', 'color' => '#dbeafe', 'priority' => 5],
            ['name' => 'HelloKtown', 'name_en' => 'Hello Ktown',      'slug' => 'hello-ktown',   'icon' => '🏘️', 'color' => '#fef3c7', 'priority' => 6],
            ['name' => '핫딜',       'name_en' => 'Hot Deals',        'slug' => 'hot-deals',     'icon' => '🔥', 'color' => '#fee2e2', 'priority' => 7],
            ['name' => '교육',       'name_en' => 'Education',        'slug' => 'education',     'icon' => '📚', 'color' => '#ede9fe', 'priority' => 8],
            ['name' => '의료/건강',  'name_en' => 'Health',           'slug' => 'health',        'icon' => '🏥', 'color' => '#d1fae5', 'priority' => 9],
        ];

        $subCategories = [
            // 사회 (slug: society)
            'society' => [
                ['name' => '사회',          'slug' => 'society-general',   'priority' => 1],
                ['name' => '사건사고',       'slug' => 'incidents',          'priority' => 2],
                ['name' => '사람/커뮤니티',  'slug' => 'community-people',   'priority' => 3],
                ['name' => '이민/비자',      'slug' => 'immigration',        'priority' => 4],
                ['name' => '교육',          'slug' => 'society-education',  'priority' => 5],
                ['name' => '정치',          'slug' => 'politics',           'priority' => 6],
                ['name' => '국제',          'slug' => 'international',      'priority' => 7],
                ['name' => '오피니언',       'slug' => 'opinion',            'priority' => 8],
            ],
            // 경제
            'economy' => [
                ['name' => '경제',          'slug' => 'economy-general',    'priority' => 1],
                ['name' => '비즈니스',       'slug' => 'business',           'priority' => 2],
                ['name' => '부동산',         'slug' => 'economy-realestate', 'priority' => 3],
                ['name' => '금융/투자',      'slug' => 'finance-investment', 'priority' => 4],
                ['name' => '취업/창업',      'slug' => 'jobs-startup',       'priority' => 5],
                ['name' => '소비자',         'slug' => 'consumer',           'priority' => 6],
                ['name' => '세금',          'slug' => 'tax',                'priority' => 7],
            ],
            // 라이프
            'life' => [
                ['name' => '라이프/레저',   'slug' => 'life-leisure',        'priority' => 1],
                ['name' => '건강',          'slug' => 'life-health',         'priority' => 2],
                ['name' => '종교',          'slug' => 'religion',            'priority' => 3],
                ['name' => '여행·취미',     'slug' => 'travel-hobby',        'priority' => 4],
                ['name' => '리빙·스타일',   'slug' => 'living-style',        'priority' => 5],
                ['name' => '문화·예술',     'slug' => 'culture-arts',        'priority' => 6],
                ['name' => '시니어',        'slug' => 'senior',              'priority' => 7],
            ],
            // 연예/스포츠
            'entertainment' => [
                ['name' => '방송/연예',     'slug' => 'broadcast-celebrity', 'priority' => 1],
                ['name' => '영화',          'slug' => 'movies',              'priority' => 2],
                ['name' => '스포츠',        'slug' => 'sports-general',      'priority' => 3],
                ['name' => '한국야구',      'slug' => 'korea-baseball',      'priority' => 4],
                ['name' => 'MLB',          'slug' => 'mlb',                 'priority' => 5],
                ['name' => '농구',          'slug' => 'basketball',          'priority' => 6],
                ['name' => '풋볼',          'slug' => 'football',            'priority' => 7],
                ['name' => '골프',          'slug' => 'golf',                'priority' => 8],
                ['name' => '축구',          'slug' => 'soccer',              'priority' => 9],
            ],
            // ASK미국
            'ask-america' => [
                ['name' => '이민법',        'slug' => 'immigration-law',     'priority' => 1],
                ['name' => '세금/회계',     'slug' => 'tax-accounting',      'priority' => 2],
                ['name' => '의료/보험',     'slug' => 'medical-insurance',   'priority' => 3],
                ['name' => '부동산/법률',   'slug' => 'realestate-law',      'priority' => 4],
                ['name' => '교육/유학',     'slug' => 'education-study',     'priority' => 5],
                ['name' => '생활정보',      'slug' => 'life-info',           'priority' => 6],
            ],
            // HelloKtown
            'hello-ktown' => [
                ['name' => '코리아타운소식', 'slug' => 'ktown-news',          'priority' => 1],
                ['name' => '맛집/카페',     'slug' => 'restaurants-cafe',    'priority' => 2],
                ['name' => '뷰티/패션',     'slug' => 'beauty-fashion',      'priority' => 3],
                ['name' => '커뮤니티행사',  'slug' => 'community-events',    'priority' => 4],
                ['name' => '비즈니스탐방',  'slug' => 'business-visit',      'priority' => 5],
            ],
            // 핫딜
            'hot-deals' => [
                ['name' => '식품/마트',     'slug' => 'food-market',         'priority' => 1],
                ['name' => '가전/전자',     'slug' => 'electronics',         'priority' => 2],
                ['name' => '의류/패션',     'slug' => 'clothing-fashion',    'priority' => 3],
                ['name' => '여행/숙박',     'slug' => 'travel-hotel',        'priority' => 4],
                ['name' => '맛집할인',      'slug' => 'restaurant-discount', 'priority' => 5],
                ['name' => '기타핫딜',      'slug' => 'other-deals',         'priority' => 6],
            ],
            // 교육
            'education' => [
                ['name' => '유아교육',      'slug' => 'early-childhood',     'priority' => 1],
                ['name' => '초중고',        'slug' => 'k12',                 'priority' => 2],
                ['name' => '대학/대학원',   'slug' => 'college',             'priority' => 3],
                ['name' => '유학',          'slug' => 'study-abroad',        'priority' => 4],
                ['name' => '특기/예능',     'slug' => 'arts-talent',         'priority' => 5],
                ['name' => '교육정보',      'slug' => 'education-info',      'priority' => 6],
            ],
            // 의료/건강
            'health' => [
                ['name' => '한방/침술',     'slug' => 'oriental-medicine',   'priority' => 1],
                ['name' => '내과/외과',     'slug' => 'internal-surgery',    'priority' => 2],
                ['name' => '치과/안과',     'slug' => 'dental-eye',          'priority' => 3],
                ['name' => '정신건강',      'slug' => 'mental-health',       'priority' => 4],
                ['name' => '건강식품',      'slug' => 'health-food',         'priority' => 5],
                ['name' => '운동/피트니스', 'slug' => 'exercise-fitness',    'priority' => 6],
            ],
        ];

        // 메인 카테고리 생성
        $mainMap = [];
        foreach ($mainCategories as $mainData) {
            $cat = NewsCategory::create([
                'name'      => $mainData['name'],
                'name_en'   => $mainData['name_en'],
                'slug'      => $mainData['slug'],
                'parent_id' => null,
                'priority'  => $mainData['priority'],
                'is_active' => true,
                'icon'      => $mainData['icon'],
                'color'     => $mainData['color'],
            ]);
            $mainMap[$mainData['slug']] = $cat->id;
        }

        // 서브 카테고리 생성
        foreach ($subCategories as $parentSlug => $subs) {
            $parentId = $mainMap[$parentSlug] ?? null;
            if (!$parentId) continue;

            foreach ($subs as $subData) {
                NewsCategory::create([
                    'name'      => $subData['name'],
                    'name_en'   => null,
                    'slug'      => $subData['slug'],
                    'parent_id' => $parentId,
                    'priority'  => $subData['priority'],
                    'is_active' => true,
                    'icon'      => null,
                    'color'     => null,
                ]);
            }
        }

        $this->command->info('NewsCategorySeeder 완료: ' . NewsCategory::count() . '개 카테고리 생성');
    }
}
