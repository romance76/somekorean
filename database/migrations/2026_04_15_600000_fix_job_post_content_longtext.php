<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        // 리치에디터의 base64 이미지로 TEXT(64KB) 초과하는 문제 해결
        if (Schema::hasTable('job_posts')) {
            DB::statement('ALTER TABLE job_posts MODIFY content LONGTEXT NOT NULL');
        }
        // 이력서도 동일 이슈 방지
        if (Schema::hasTable('resumes')) {
            DB::statement('ALTER TABLE resumes MODIFY summary LONGTEXT NULL');
            DB::statement('ALTER TABLE resumes MODIFY experience LONGTEXT NULL');
        }
        // 연락처 전화번호 길이 여유(20 → 30) — "213-000-0000 (ext.123)" 같은 입력 방지
        if (Schema::hasTable('job_posts')) {
            DB::statement('ALTER TABLE job_posts MODIFY contact_phone VARCHAR(30) NULL');
        }
    }

    public function down(): void
    {
        // 되돌리지 않음 (데이터 손실 방지)
    }
};
