<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('banner_ads', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');                           // 광고 제목
            $table->string('image_url');                       // 배너 이미지
            $table->string('link_url')->nullable();            // 클릭 시 이동 URL
            $table->string('page', 30);                        // 노출 페이지: home, market, jobs, directory, news, qa, recipes, community, all
            $table->string('position', 20);                    // 위치: top, left, center, right
            $table->string('geo_scope', 20)->default('all');   // 지역 범위: all, state, county, city
            $table->string('geo_value')->nullable();           // 지역 값: CA, Gwinnett, Suwanee 등
            $table->date('start_date');
            $table->date('end_date');
            $table->unsignedInteger('daily_cost')->default(0); // 일일 포인트 비용
            $table->unsignedInteger('total_cost')->default(0); // 총 비용
            $table->unsignedInteger('impressions')->default(0);
            $table->unsignedInteger('clicks')->default(0);
            $table->string('status', 20)->default('pending');  // pending, active, rejected, expired, paused
            $table->text('reject_reason')->nullable();
            $table->timestamps();
            $table->index(['status', 'start_date', 'end_date']);
            $table->index(['page', 'position']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('banner_ads');
    }
};
