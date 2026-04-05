<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ShoppingSeeder extends Seeder
{
    public function run(): void
    {
        // ── 1. Seed Shopping Stores ────────────────────────────────────────────
        $stores = [
            // 한인마트 (Korean)
            ['name' => 'H마트 (H-Mart)',       'type' => 'korean',   'region' => 'National', 'website' => 'https://www.hmart.com',     'description' => '미국 최대 한인 슈퍼마켓 체인', 'logo' => null],
            ['name' => 'Zion Market',           'type' => 'korean',   'region' => 'CA',       'website' => 'https://www.zionmarket.com','description' => '캘리포니아 대형 한인마트',      'logo' => null],
            ['name' => 'KoreaTown Galleria',    'type' => 'korean',   'region' => 'CA',       'website' => null,                        'description' => 'LA 코리아타운 갈레리아 마켓',  'logo' => null],
            ['name' => 'Hannam Chain',          'type' => 'korean',   'region' => 'CA',       'website' => null,                        'description' => '한남체인 슈퍼마켓',             'logo' => null],
            ['name' => 'Assi Plaza',            'type' => 'korean',   'region' => 'National', 'website' => null,                        'description' => '아씨 플라자 한인마트',          'logo' => null],
            // 미국마트 (American)
            ['name' => 'Costco',                'type' => 'american', 'region' => 'National', 'website' => 'https://www.costco.com',    'description' => '대형 창고형 할인매장',          'logo' => null],
            ['name' => 'Walmart',               'type' => 'american', 'region' => 'National', 'website' => 'https://www.walmart.com',   'description' => '미국 최대 유통업체',            'logo' => null],
            ['name' => 'Target',                'type' => 'american', 'region' => 'National', 'website' => 'https://www.target.com',    'description' => '타겟 대형마트',                 'logo' => null],
            ['name' => 'Trader Joe\'s',         'type' => 'american', 'region' => 'National', 'website' => 'https://www.traderjoes.com','description' => '건강식품 전문 슈퍼마켓',       'logo' => null],
            ['name' => 'Whole Foods Market',    'type' => 'american', 'region' => 'National', 'website' => 'https://www.wholefoodsmarket.com', 'description' => '유기농 식품 전문점', 'logo' => null],
            // 아시안마트 (Asian)
            ['name' => '99 Ranch Market',       'type' => 'asian',    'region' => 'National', 'website' => 'https://www.99ranch.com',   'description' => '대형 아시안 슈퍼마켓',         'logo' => null],
            ['name' => 'Mitsuwa Marketplace',   'type' => 'asian',    'region' => 'CA',       'website' => 'https://www.mitsuwa.com',   'description' => '일본 식품 전문 마트',           'logo' => null],
            ['name' => 'Manila Oriental Market','type' => 'asian',    'region' => 'National', 'website' => null,                        'description' => '필리핀/동남아 식품 마트',       'logo' => null],
        ];

        $storeIds = [];
        foreach ($stores as $store) {
            $existing = DB::table('shopping_stores')->where('name', $store['name'])->first();
            if (!$existing) {
                $id = DB::table('shopping_stores')->insertGetId(array_merge($store, [
                    'is_active'  => true,
                    'created_at' => now(),
                    'updated_at' => now(),
                ]));
                $storeIds[$store['name']] = $id;
            } else {
                $storeIds[$store['name']] = $existing->id;
            }
        }

        // ── 2. Seed Shopping Deals ─────────────────────────────────────────────
        $now = now();
        $validFrom = $now->toDateString();
        $validUntil = $now->addDays(7)->toDateString();

        $deals = [
            // H-Mart
            ['store' => 'H마트 (H-Mart)', 'title' => '농심 신라면 멀티팩 (5봉)', 'description' => '한국 대표 라면 5봉 세트', 'original_price' => 5.99, 'sale_price' => 3.99, 'category' => '식품/음료', 'image_url' => null],
            ['store' => 'H마트 (H-Mart)', 'title' => '청정원 고추장 (500g)', 'description' => '한국 전통 고추장', 'original_price' => 8.99, 'sale_price' => 6.49, 'category' => '식품/음료', 'image_url' => null],
            ['store' => 'H마트 (H-Mart)', 'title' => '오뚜기 카레 (3인분 x3)', 'description' => '즉석 카레 멀티팩', 'original_price' => 6.99, 'sale_price' => 4.99, 'category' => '식품/음료', 'image_url' => null],
            ['store' => 'H마트 (H-Mart)', 'title' => '한우 불고기 (1lb)', 'description' => '양념 불고기용 소고기', 'original_price' => 18.99, 'sale_price' => 14.99, 'category' => '정육/수산', 'image_url' => null],
            ['store' => 'H마트 (H-Mart)', 'title' => '비비고 왕교자 만두 (24개입)', 'description' => '인기 냉동 왕교자 만두', 'original_price' => 12.99, 'sale_price' => 9.99, 'category' => '냉동식품', 'image_url' => null],
            // Zion Market
            ['store' => 'Zion Market', 'title' => '삼겹살 특가 (2lb)', 'description' => '신선한 삼겹살 주간 특가', 'original_price' => 22.99, 'sale_price' => 16.99, 'category' => '정육/수산', 'image_url' => null],
            ['store' => 'Zion Market', 'title' => '김치 (한국산 1.5kg)', 'description' => '국내산 배추 포기김치', 'original_price' => 19.99, 'sale_price' => 14.99, 'category' => '식품/음료', 'image_url' => null],
            ['store' => 'Zion Market', 'title' => '두부 멀티팩 (4개입)', 'description' => '순두부/연두부 세트', 'original_price' => 7.99, 'sale_price' => 5.99, 'category' => '식품/음료', 'image_url' => null],
            // Costco
            ['store' => 'Costco', 'title' => 'Kirkland 유기농 달걀 (24개)', 'description' => '유기농 대란 24개입', 'original_price' => 9.99, 'sale_price' => 7.49, 'category' => '유제품', 'image_url' => null],
            ['store' => 'Costco', 'title' => 'Kirkland 연어 (3lbs)', 'description' => '아틀란틱 연어 대용량', 'original_price' => 29.99, 'sale_price' => 24.99, 'category' => '정육/수산', 'image_url' => null],
            ['store' => 'Costco', 'title' => 'Starbucks 홀빈 커피 (2.5lb)', 'description' => '스타벅스 하우스 블렌드 대용량', 'original_price' => 24.99, 'sale_price' => 19.99, 'category' => '식품/음료', 'image_url' => null],
            ['store' => 'Costco', 'title' => 'Apple AirPods Pro (2세대)', 'description' => 'ANC 무선 이어폰', 'original_price' => 249.00, 'sale_price' => 189.99, 'category' => '전자기기', 'image_url' => null],
            // Walmart
            ['store' => 'Walmart', 'title' => 'Tide 세탁세제 (146oz)', 'description' => '타이드 대용량 액체 세제', 'original_price' => 24.97, 'sale_price' => 18.97, 'category' => '생활용품', 'image_url' => null],
            ['store' => 'Walmart', 'title' => 'LG 55인치 4K TV', 'description' => 'LG UHD 4K 스마트 TV', 'original_price' => 699.00, 'sale_price' => 448.00, 'category' => '전자기기', 'image_url' => null],
            // Target
            ['store' => 'Target', 'title' => 'Dyson V8 무선청소기', 'description' => '다이슨 V8 코드리스 진공청소기', 'original_price' => 449.99, 'sale_price' => 299.99, 'category' => '생활용품', 'image_url' => null],
            ['store' => 'Target', 'title' => 'Levi\'s 청바지 (남/여)', 'description' => '리바이스 클래식 청바지 30% 할인', 'original_price' => 69.99, 'sale_price' => 48.99, 'category' => '패션/의류', 'image_url' => null],
            // 99 Ranch
            ['store' => '99 Ranch Market', 'title' => '쌀 자스민 (25lb)', 'description' => '태국산 재스민 쌀 대용량', 'original_price' => 26.99, 'sale_price' => 19.99, 'category' => '식품/음료', 'image_url' => null],
            ['store' => '99 Ranch Market', 'title' => '새우 (21-25 size, 2lb)', 'description' => '냉동 새우 대용량 팩', 'original_price' => 18.99, 'sale_price' => 12.99, 'category' => '정육/수산', 'image_url' => null],
            // Trader Joe's
            ['store' => 'Trader Joe\'s', 'title' => 'Mandarin Orange 치킨', 'description' => '인기 냉동 만다린 오렌지 치킨', 'original_price' => 6.49, 'sale_price' => 4.99, 'category' => '냉동식품', 'image_url' => null],
            ['store' => 'Trader Joe\'s', 'title' => '유기농 후무스 (10oz)', 'description' => '유기농 클래식 후무스', 'original_price' => 4.99, 'sale_price' => 3.49, 'category' => '식품/음료', 'image_url' => null],
        ];

        foreach ($deals as $deal) {
            $storeId = $storeIds[$deal['store']] ?? null;
            if (!$storeId) continue;

            $discountPct = null;
            if ($deal['original_price'] > 0) {
                $discountPct = (int) round((1 - $deal['sale_price'] / $deal['original_price']) * 100);
            }

            $existing = DB::table('shopping_deals')
                ->where('title', $deal['title'])
                ->where('store_id', $storeId)
                ->first();

            if (!$existing) {
                DB::table('shopping_deals')->insert([
                    'store_id'       => $storeId,
                    'title'          => $deal['title'],
                    'description'    => $deal['description'],
                    'image_url'      => $deal['image_url'],
                    'original_price' => $deal['original_price'],
                    'sale_price'     => $deal['sale_price'],
                    'discount_percent' => $discountPct,
                    'category'       => $deal['category'],
                    'is_active'      => true,
                    'is_featured'    => $discountPct >= 30 ? 1 : 0,
                    'valid_from'     => $validFrom,
                    'valid_until'    => $validUntil,
                    'url'            => 'https://somekorean.com/shopping/deal-' . rand(10000,99999),
                    'source'         => '시드데이터',
                    'created_at'     => now(),
                    'updated_at'     => now(),
                ]);
            }
        }

        // ── 3. Link existing Slickdeals records to Walmart (american) store ───
        $walmartId = $storeIds['Walmart'] ?? null;
        if ($walmartId) {
            DB::table('shopping_deals')
                ->where('source', 'Slickdeals')
                ->whereNull('store_id')
                ->update(['store_id' => $walmartId, 'valid_from' => $validFrom, 'valid_until' => $validUntil]);
        }

        $this->command->info('쇼핑 스토어 및 딜 시딩 완료');
    }
}
