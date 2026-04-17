<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // qa_answers에 dislike_count 추가
        if (!Schema::hasColumn('qa_answers', 'dislike_count')) {
            Schema::table('qa_answers', function (Blueprint $table) {
                $table->unsignedInteger('dislike_count')->default(0)->after('like_count');
            });
        }

        // qa_answer_likes에 type 추가 (like/dislike)
        if (!Schema::hasColumn('qa_answer_likes', 'type')) {
            Schema::table('qa_answer_likes', function (Blueprint $table) {
                $table->string('type', 10)->default('like')->after('user_id');
            });
        }
    }

    public function down(): void
    {
        Schema::table('qa_answers', function (Blueprint $table) {
            $table->dropColumn('dislike_count');
        });
        Schema::table('qa_answer_likes', function (Blueprint $table) {
            $table->dropColumn('type');
        });
    }
};
