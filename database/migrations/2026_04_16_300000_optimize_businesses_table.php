<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        // 1. 인덱스 추가 (없으면)
        Schema::table('businesses', function (Blueprint $table) {
            // rating 정렬용
            if (!$this->hasIndex('businesses', 'businesses_rating_index')) {
                $table->index('rating');
            }
            // review_count 정렬용
            if (!$this->hasIndex('businesses', 'businesses_review_count_index')) {
                $table->index('review_count');
            }
            // view_count 정렬용
            if (!$this->hasIndex('businesses', 'businesses_view_count_index')) {
                $table->index('view_count');
            }
            // state 필터용
            if (!$this->hasIndex('businesses', 'businesses_state_index')) {
                $table->index('state');
            }
            // google_place_id 중복 체크용
            if (!$this->hasIndex('businesses', 'businesses_google_place_id_index')) {
                $table->index('google_place_id');
            }
        });

        // 2. 오늘 생성된 중복 데이터 제거 (google_place_id 기준, 오래된 것 유지)
        $today = now()->toDateString();
        $duplicates = DB::select("
            SELECT b1.id FROM businesses b1
            INNER JOIN businesses b2
                ON b1.google_place_id = b2.google_place_id
                AND b1.id > b2.id
            WHERE b1.google_place_id IS NOT NULL
              AND b1.google_place_id != ''
              AND DATE(b1.created_at) = ?
        ", [$today]);

        if (count($duplicates) > 0) {
            $ids = array_map(fn($d) => $d->id, $duplicates);
            DB::table('businesses')->whereIn('id', $ids)->delete();
        }
    }

    public function down(): void
    {
        Schema::table('businesses', function (Blueprint $table) {
            $table->dropIndex(['rating']);
            $table->dropIndex(['review_count']);
            $table->dropIndex(['view_count']);
            $table->dropIndex(['state']);
        });
    }

    private function hasIndex(string $table, string $indexName): bool
    {
        $indexes = DB::select("SHOW INDEX FROM {$table} WHERE Key_name = ?", [$indexName]);
        return count($indexes) > 0;
    }
};
