<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('comments', function (Blueprint $table) {
            // post_id를 nullable로 변경 (다양한 콘텐츠 타입 댓글 지원)
            $table->unsignedBigInteger('post_id')->nullable()->change();
            // 다형성 참조 컬럼 추가
            $table->string('commentable_type', 100)->nullable()->after('post_id');
            $table->unsignedBigInteger('commentable_id')->nullable()->after('commentable_type');
            $table->index(['commentable_type', 'commentable_id'], 'comments_commentable_index');
        });
    }

    public function down(): void
    {
        Schema::table('comments', function (Blueprint $table) {
            $table->dropIndex('comments_commentable_index');
            $table->dropColumn(['commentable_type', 'commentable_id']);
            $table->unsignedBigInteger('post_id')->nullable(false)->change();
        });
    }
};
