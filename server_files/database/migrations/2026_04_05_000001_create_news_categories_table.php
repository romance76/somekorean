<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('news_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name');           // 한글 이름
            $table->string('name_en')->nullable(); // 영문 이름
            $table->string('slug')->unique(); // URL-friendly slug
            $table->unsignedBigInteger('parent_id')->nullable(); // null이면 메인 카테고리
            $table->integer('priority')->default(0); // 정렬 순서
            $table->boolean('is_active')->default(true);
            $table->string('icon')->nullable();  // 이모지 아이콘
            $table->string('color')->nullable(); // 색상 hex
            $table->timestamps();

            $table->foreign('parent_id')->references('id')->on('news_categories')->onDelete('set null');
            $table->index('parent_id');
            $table->index('priority');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('news_categories');
    }
};
