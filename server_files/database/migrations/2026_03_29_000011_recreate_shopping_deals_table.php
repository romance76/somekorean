<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // 구버전 스키마(store_id 필수 등)가 있으면 드롭 후 재생성
        if (Schema::hasTable('shopping_deals') && !Schema::hasColumn('shopping_deals', 'url')) {
            Schema::drop('shopping_deals');
        }

        if (!Schema::hasTable('shopping_deals')) {
            Schema::create('shopping_deals', function (Blueprint $table) {
                $table->id();
                $table->string('title');
                $table->text('description')->nullable();
                $table->string('url', 500)->unique();
                $table->string('source')->default('');
                $table->string('price')->nullable();
                $table->decimal('original_price', 10, 2)->nullable();
                $table->decimal('sale_price', 10, 2)->nullable();
                $table->integer('discount_percent')->nullable();
                $table->string('image_url')->nullable();
                $table->string('category')->default('기타');
                $table->string('store')->nullable();
                $table->boolean('is_active')->default(true);
                $table->boolean('is_featured')->default(false);
                $table->timestamp('expires_at')->nullable();
                $table->timestamp('published_at')->nullable();
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('shopping_deals');
    }
};
