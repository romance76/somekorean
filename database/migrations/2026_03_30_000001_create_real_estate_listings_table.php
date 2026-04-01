<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('real_estate_listings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->text('description')->nullable();
            $table->enum('type', ['렌트', '매매', '룸메이트', '상가', '전세'])->default('렌트');
            $table->decimal('price', 12, 2)->nullable();
            $table->decimal('deposit', 12, 2)->nullable();
            $table->string('address')->nullable();
            $table->string('region')->nullable();
            $table->decimal('latitude', 10, 7)->nullable();
            $table->decimal('longitude', 10, 7)->nullable();
            $table->unsignedTinyInteger('bedrooms')->nullable();
            $table->unsignedTinyInteger('bathrooms')->nullable();
            $table->unsignedInteger('sqft')->nullable();
            $table->json('photos')->nullable();
            $table->string('move_in_date')->nullable();
            $table->enum('pet_policy', ['가능', '불가', '협의'])->default('협의');
            $table->string('phone')->nullable();
            $table->string('email')->nullable();
            $table->boolean('is_pinned')->default(false);
            $table->unsignedBigInteger('view_count')->default(0);
            $table->enum('status', ['active', 'closed', 'deleted'])->default('active');
            $table->timestamps();
            $table->softDeletes();
            $table->index(['status', 'type']);
            $table->index(['region']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('real_estate_listings');
    }
};

