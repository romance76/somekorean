<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * 중고장터 홀드 + 상위노출(부스트) 시스템
 *
 * 홀드: 구매자가 포인트로 물건을 예약. 6시간 단위 과금.
 *   - 90% 판매자, 10% 운영자 수수료
 * 부스트: 판매자가 포인트로 리스트 상위 노출. 하루 100포인트.
 */
return new class extends Migration {
    public function up(): void
    {
        // market_items 에 홀드/부스트 옵션 추가
        Schema::table('market_items', function (Blueprint $table) {
            $table->boolean('hold_enabled')->default(false)->after('is_negotiable');
            $table->unsignedInteger('hold_price_per_6h')->default(0)->after('hold_enabled');       // 6시간당 포인트
            $table->unsignedInteger('hold_max_hours')->default(24)->after('hold_price_per_6h');     // 최대 홀드 시간 (6~168)
            $table->timestamp('boosted_until')->nullable()->after('hold_max_hours');                 // 상위노출 만료
        });

        // market_reservations 에 홀드 상세 정보 추가
        Schema::table('market_reservations', function (Blueprint $table) {
            $table->timestamp('hold_until')->nullable()->after('points_held');           // 홀드 만료 시간
            $table->unsignedInteger('hold_hours')->default(0)->after('hold_until');      // 요청한 홀드 시간
            $table->unsignedInteger('commission')->default(0)->after('hold_hours');      // 운영자 수수료 (10%)
            $table->unsignedInteger('seller_received')->default(0)->after('commission'); // 판매자 수령 (90%)
        });
    }

    public function down(): void
    {
        Schema::table('market_items', function (Blueprint $table) {
            $table->dropColumn(['hold_enabled', 'hold_price_per_6h', 'hold_max_hours', 'boosted_until']);
        });
        Schema::table('market_reservations', function (Blueprint $table) {
            $table->dropColumn(['hold_until', 'hold_hours', 'commission', 'seller_received']);
        });
    }
};
