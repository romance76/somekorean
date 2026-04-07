<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('poker_tournaments', function (Blueprint $table) {
            $table->json('schedule_pattern')->nullable()->after('bounty_pct');
            // schedule_pattern: { "recurring": true, "days": ["mon","tue",...], "time": "18:00" }
            // null = 일회성, json = 반복 스케줄
            $table->boolean('is_template')->default(false)->after('schedule_pattern');
            // is_template: true면 자동 생성 템플릿
        });
    }

    public function down(): void
    {
        Schema::table('poker_tournaments', function (Blueprint $table) {
            $table->dropColumn(['schedule_pattern', 'is_template']);
        });
    }
};
