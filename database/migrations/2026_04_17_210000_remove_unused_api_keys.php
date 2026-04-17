<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * 미구현 API 키 row 제거 (2026-04-17 Phase 2-C 묶음 1)
 * - Spoonacular / Eventbrite / OpenAI: grep 결과 실 사용처 없음
 * - api_keys 테이블 자체는 유지 (다른 서비스 사용 중)
 * - site_settings 의 JSON blob api_keys 는 별도 정리
 */
return new class extends Migration {
    public function up(): void
    {
        if (Schema::hasTable('api_keys')) {
            DB::table('api_keys')
                ->whereIn('service', ['openai', 'spoonacular', 'eventbrite', 'eventbrite_oauth', 'eventbrite_token'])
                ->delete();
        }

        // site_settings 에 저장된 개별 키들도 정리 (값 삭제, row 유지는 무의미)
        if (Schema::hasTable('site_settings')) {
            DB::table('site_settings')
                ->whereIn('key', [
                    'spoonacular_api_key',
                    'eventbrite_api_key',
                    'eventbrite_oauth_secret',
                    'eventbrite_private_token',
                    'openai_api_key',
                ])
                ->delete();
        }
    }

    public function down(): void
    {
        // 롤백 시 사이트 셋팅 빈 값으로 복원 (실제 키는 .env/backup 에서 복구)
        if (Schema::hasTable('site_settings')) {
            foreach (['spoonacular_api_key','eventbrite_api_key','openai_api_key'] as $k) {
                DB::table('site_settings')->updateOrInsert(
                    ['key' => $k],
                    ['value' => null, 'group' => 'general', 'updated_at' => now(), 'created_at' => now()]
                );
            }
        }
    }
};
