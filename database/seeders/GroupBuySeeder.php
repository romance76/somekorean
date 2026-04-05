<?php

namespace Database\Seeders;

use App\Models\GroupBuy;
use App\Models\User;
use Illuminate\Database\Seeder;

class GroupBuySeeder extends Seeder
{
    public function run(): void
    {
        $userIds = User::pluck('id')->toArray();
        if (empty($userIds)) { $this->command->warn('GroupBuySeeder: no users, skipping.'); return; }

        $products = [
            ['title' => '코스트코 한우 갈비 공구', 'orig' => 8999, 'group' => 6999, 'min' => 5, 'max' => 20],
            ['title' => '김치냉장고 공동구매', 'orig' => 199900, 'group' => 149900, 'min' => 3, 'max' => 10],
            ['title' => '한국 라면 박스 공구', 'orig' => 2500, 'group' => 1800, 'min' => 10, 'max' => 50],
            ['title' => '에어프라이어 공동구매', 'orig' => 12999, 'group' => 8999, 'min' => 5, 'max' => 15],
            ['title' => '한국 화장품 세트 공구', 'orig' => 7999, 'group' => 4999, 'min' => 5, 'max' => 30],
            ['title' => '한복 공동구매 (아동용)', 'orig' => 4999, 'group' => 2999, 'min' => 10, 'max' => 30],
            ['title' => '한국 과자 박스 공구', 'orig' => 3500, 'group' => 2200, 'min' => 10, 'max' => 40],
            ['title' => '다이슨 청소기 공동구매', 'orig' => 49999, 'group' => 39999, 'min' => 3, 'max' => 10],
            ['title' => '한국 소주/맥주 세트 공구', 'orig' => 4999, 'group' => 3499, 'min' => 10, 'max' => 30],
            ['title' => '삼성 TV 65인치 공동구매', 'orig' => 89999, 'group' => 69999, 'min' => 3, 'max' => 5],
            ['title' => '유기농 쌀 10kg 공동구매', 'orig' => 3999, 'group' => 2799, 'min' => 10, 'max' => 30],
            ['title' => '한국 건강식품 세트 공구', 'orig' => 5999, 'group' => 3999, 'min' => 5, 'max' => 20],
            ['title' => '로봇 청소기 공동구매', 'orig' => 29999, 'group' => 19999, 'min' => 5, 'max' => 15],
            ['title' => '한국 참기름 세트 공구', 'orig' => 2999, 'group' => 1999, 'min' => 10, 'max' => 40],
            ['title' => '어린이 한글 교재 세트', 'orig' => 6999, 'group' => 4499, 'min' => 5, 'max' => 20],
            ['title' => '닌텐도 스위치 공동구매', 'orig' => 29999, 'group' => 24999, 'min' => 3, 'max' => 10],
            ['title' => '한국 김 선물세트 공구', 'orig' => 2499, 'group' => 1599, 'min' => 10, 'max' => 50],
            ['title' => '전기밥솥 쿠쿠 공동구매', 'orig' => 19999, 'group' => 14999, 'min' => 5, 'max' => 10],
            ['title' => '한국 떡 세트 공동구매', 'orig' => 3499, 'group' => 2299, 'min' => 10, 'max' => 30],
            ['title' => '캠핑 장비 세트 공구', 'orig' => 15999, 'group' => 10999, 'min' => 5, 'max' => 15],
            ['title' => '한국 홍삼 세트 공동구매', 'orig' => 12999, 'group' => 8999, 'min' => 5, 'max' => 20],
            ['title' => '아이패드 케이스 공구', 'orig' => 3999, 'group' => 2499, 'min' => 10, 'max' => 30],
            ['title' => '한국 된장/고추장 세트', 'orig' => 2999, 'group' => 1999, 'min' => 10, 'max' => 40],
            ['title' => '키즈 수영복 공동구매', 'orig' => 2499, 'group' => 1599, 'min' => 10, 'max' => 30],
            ['title' => '한국 반찬 밀키트 공구', 'orig' => 4999, 'group' => 3499, 'min' => 5, 'max' => 20],
        ];

        $contentTemplate = "{title}\n\n공동구매 진행합니다!\n\n정가: \${orig}\n공구가: \${group}\n할인율: {discount}%\n\n최소 인원: {min}명\n최대 인원: {max}명\n\n관심 있으신 분은 참여해 주세요!\n마감일까지 최소 인원이 모이면 진행됩니다.\n\n배송지: {city} 지역\n문의사항은 댓글로 남겨주세요.";

        $cities = [
            ['city' => 'Los Angeles',   'state' => 'CA', 'lat' => 34.0522,  'lng' => -118.2437],
            ['city' => 'New York',      'state' => 'NY', 'lat' => 40.7128,  'lng' => -74.0060],
            ['city' => 'Chicago',       'state' => 'IL', 'lat' => 41.8781,  'lng' => -87.6298],
            ['city' => 'Atlanta',       'state' => 'GA', 'lat' => 33.7490,  'lng' => -84.3880],
            ['city' => 'Dallas',        'state' => 'TX', 'lat' => 32.7767,  'lng' => -96.7970],
            ['city' => 'Houston',       'state' => 'TX', 'lat' => 29.7604,  'lng' => -95.3698],
            ['city' => 'Seattle',       'state' => 'WA', 'lat' => 47.6062,  'lng' => -122.3321],
            ['city' => 'San Francisco', 'state' => 'CA', 'lat' => 37.7749,  'lng' => -122.4194],
        ];

        $statuses = ['recruiting', 'recruiting', 'recruiting', 'recruiting', 'confirmed', 'completed', 'cancelled'];
        $now = now();
        $rows = [];

        for ($i = 0; $i < 100; $i++) {
            $product = $products[$i % count($products)];
            $city    = $cities[array_rand($cities)];
            $status  = $statuses[array_rand($statuses)];

            $current = $status === 'recruiting' ? rand(0, $product['min']) : ($status === 'confirmed' || $status === 'completed' ? rand($product['min'], $product['max']) : rand(0, 3));
            $discount = round((1 - $product['group'] / $product['orig']) * 100);

            $content = str_replace(
                ['{title}', '{orig}', '{group}', '{discount}', '{min}', '{max}', '{city}'],
                [$product['title'], number_format($product['orig'] / 100, 2), number_format($product['group'] / 100, 2), $discount, $product['min'], $product['max'], $city['city']],
                $contentTemplate
            );

            $rows[] = [
                'user_id'              => $userIds[array_rand($userIds)],
                'title'                => $product['title'],
                'content'              => $content,
                'images'               => null,
                'product_url'          => null,
                'original_price'       => $product['orig'],
                'group_price'          => $product['group'],
                'min_participants'     => $product['min'],
                'max_participants'     => $product['max'],
                'current_participants' => $current,
                'lat'                  => round($city['lat'] + rand(-200, 200) / 10000, 7),
                'lng'                  => round($city['lng'] + rand(-200, 200) / 10000, 7),
                'city'                 => $city['city'],
                'state'                => $city['state'],
                'status'               => $status,
                'deadline'             => $status === 'recruiting' ? $now->copy()->addDays(rand(3, 14)) : $now->copy()->subDays(rand(1, 30)),
                'created_at'           => $now->copy()->subDays(rand(0, 60))->subHours(rand(0, 23)),
                'updated_at'           => $now,
            ];
        }

        foreach (array_chunk($rows, 50) as $chunk) {
            GroupBuy::insert($chunk);
        }

        $this->command->info('GroupBuySeeder: 100 group buys created');
    }
}
