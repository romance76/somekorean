<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('api_keys', function (Blueprint $table) {
            $table->id();
            $table->string('name');             // 서비스 이름 (예: "아리랑 뉴스 API")
            $table->string('service', 50);      // 서비스 코드 (예: "arirang", "youtube")
            $table->text('api_key');            // 실제 키 (암호화 저장 권장)
            $table->string('description')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        // 기존 사용 중인 API 키들 시드
        $keys = [
            ['name' => '아리랑 뉴스 API', 'service' => 'arirang_news', 'api_key' => '7085f0f04fc76341f3e69bb97bb6ef7dad61912dc6341c54aac1f0feb386c6c1', 'description' => 'data.go.kr 공공데이터 - 아리랑국제방송 뉴스기사API (2026-04-12 ~ 2028-04-12)'],
            ['name' => 'Google Maps API', 'service' => 'google_maps', 'api_key' => env('VITE_GOOGLE_MAPS_KEY', ''), 'description' => 'Google Places / Maps 업소록용'],
            ['name' => 'YouTube Data API', 'service' => 'youtube', 'api_key' => env('YOUTUBE_API_KEY', ''), 'description' => '쇼츠/음악 수집용'],
        ];

        foreach ($keys as $k) {
            if ($k['api_key']) {
                DB::table('api_keys')->insert(array_merge($k, [
                    'is_active' => true,
                    'created_at' => now(),
                    'updated_at' => now(),
                ]));
            }
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('api_keys');
    }
};
