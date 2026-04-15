<?php

namespace App\Support;

use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

/**
 * 상위노출 설정 헬퍼.
 * point_settings 테이블의 promo_* 키를 조회해서 타이어별 슬롯 수/가격을 반환.
 * 60초 캐시.
 */
class PromotionSettings
{
    private const CACHE_KEY = 'promotion_settings_v1';

    public static function all(): array
    {
        return Cache::remember(self::CACHE_KEY, 60, function () {
            $rows = DB::table('point_settings')
                ->where('category', 'promotion')
                ->pluck('value', 'key')
                ->toArray();
            return [
                'max_slots' => [
                    'national'   => (int) ($rows['promo_max_slots_national']   ?? 5),
                    'state_plus' => (int) ($rows['promo_max_slots_state_plus'] ?? 5),
                    'sponsored'  => PHP_INT_MAX, // 스폰서는 무제한
                ],
                'price_per_day' => [
                    'national'   => (int) ($rows['promo_price_national']   ?? 100),
                    'state_plus' => (int) ($rows['promo_price_state_plus'] ?? 50),
                    'sponsored'  => (int) ($rows['promo_price_sponsored']  ?? 20),
                ],
            ];
        });
    }

    public static function maxSlots(string $tier): int
    {
        return self::all()['max_slots'][$tier] ?? 5;
    }

    public static function pricePerDay(string $tier): int
    {
        return self::all()['price_per_day'][$tier] ?? 0;
    }

    public static function flush(): void
    {
        Cache::forget(self::CACHE_KEY);
    }
}
