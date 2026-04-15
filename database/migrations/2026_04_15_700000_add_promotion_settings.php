<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * 상위노출 설정 (슬롯 수, 가격) 을 point_settings 에 등록.
 * 관리자 페이지에서 수정 가능. 추후 중고장터/부동산/업소록 에서도 재사용.
 */
return new class extends Migration {
    public function up(): void
    {
        if (!Schema::hasTable('point_settings')) return;

        $rows = [
            // 슬롯 수 (카테고리별 최대)
            ['category' => 'promotion', 'key' => 'promo_max_slots_national',   'label' => '전국 상위노출 카테고리당 최대 슬롯',    'value' => '5',   'description' => '카테고리마다 동시에 활성 가능한 전국 상위노출 개수'],
            ['category' => 'promotion', 'key' => 'promo_max_slots_state_plus', 'label' => '주(State) 상위노출 카테고리당 최대 슬롯', 'value' => '5',   'description' => '카테고리 × 주 그룹별 동시에 활성 가능한 주 상위노출 개수'],

            // 하루 가격 (P)
            ['category' => 'promotion', 'key' => 'promo_price_national',   'label' => '전국 상위노출 하루 가격(P)',   'value' => '100', 'description' => 'National 상위노출 1일 포인트'],
            ['category' => 'promotion', 'key' => 'promo_price_state_plus', 'label' => '주(State) 상위노출 하루 가격(P)', 'value' => '50', 'description' => 'State+인접주 상위노출 1일 포인트'],
            ['category' => 'promotion', 'key' => 'promo_price_sponsored',  'label' => '스폰서 하루 가격(P)',           'value' => '20', 'description' => 'Sponsored (색상 강조) 1일 포인트'],
        ];

        foreach ($rows as $r) {
            DB::table('point_settings')->updateOrInsert(
                ['key' => $r['key']],
                array_merge($r, ['updated_at' => now(), 'created_at' => now()])
            );
        }
    }

    public function down(): void
    {
        if (Schema::hasTable('point_settings')) {
            DB::table('point_settings')->whereIn('key', [
                'promo_max_slots_national', 'promo_max_slots_state_plus',
                'promo_price_national', 'promo_price_state_plus', 'promo_price_sponsored',
            ])->delete();
        }
    }
};
