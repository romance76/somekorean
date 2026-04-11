<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // 기존 recipe_posts 테이블 전체 삭제 (식품안전나라 API 기반으로 재구성)
        Schema::dropIfExists('recipe_posts');

        Schema::create('recipe_posts', function (Blueprint $table) {
            $table->id();
            $table->string('source', 20)->default('foodsafety');
            $table->string('ext_id', 50)->unique()->nullable();
            $table->string('title', 200);
            $table->string('category', 50)->nullable();       // RCP_PAT2
            $table->string('cook_method', 50)->nullable();    // RCP_WAY2
            $table->text('ingredients')->nullable();          // RCP_PARTS_DTLS
            $table->string('calories', 20)->nullable();       // INFO_ENG
            $table->string('carbs', 20)->nullable();          // INFO_CAR
            $table->string('protein', 20)->nullable();        // INFO_PRO
            $table->string('fat', 20)->nullable();            // INFO_FAT
            $table->string('sodium', 20)->nullable();         // INFO_NA
            $table->json('steps')->nullable();                // MANUAL01~20 + MANUAL_IMG01~20
            $table->string('thumbnail', 500)->nullable();     // ATT_FILE_NO_MAIN
            $table->string('hash_tags', 300)->nullable();     // HASH_TAG
            $table->integer('view_count')->default(0);
            $table->integer('like_count')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->index(['category', 'is_active']);
            $table->index('title');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('recipe_posts');
    }
};
