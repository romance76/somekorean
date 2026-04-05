<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // 공동구매
        if (!Schema::hasTable('group_buys')) {
            Schema::create('group_buys', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->constrained()->cascadeOnDelete();
                $table->string('title');
                $table->text('description');
                $table->decimal('target_price', 10, 2)->default(0);
                $table->integer('min_participants')->default(2);
                $table->integer('max_participants')->nullable();
                $table->string('category')->default('general');
                $table->string('product_url')->nullable();
                $table->json('images')->nullable();
                $table->timestamp('deadline');
                $table->enum('status', ['open', 'completed', 'cancelled'])->default('open');
                $table->timestamps();
            });
        }

        if (!Schema::hasTable('group_buy_participants')) {
            Schema::create('group_buy_participants', function (Blueprint $table) {
                $table->id();
                $table->foreignId('group_buy_id')->constrained()->cascadeOnDelete();
                $table->foreignId('user_id')->constrained()->cascadeOnDelete();
                $table->integer('quantity')->default(1);
                $table->timestamps();
                $table->unique(['group_buy_id', 'user_id']);
            });
        }

        // 멘토링
        if (!Schema::hasTable('mentors')) {
            Schema::create('mentors', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->unique()->constrained()->cascadeOnDelete();
                $table->string('field'); // IT, 비즈니스, 의료, 법률 등
                $table->text('bio');
                $table->unsignedTinyInteger('years_experience')->default(0);
                $table->string('company')->nullable();
                $table->string('position')->nullable();
                $table->json('skills')->nullable();
                $table->boolean('is_available')->default(true);
                $table->timestamps();
            });
        }

        if (!Schema::hasTable('mentor_requests')) {
            Schema::create('mentor_requests', function (Blueprint $table) {
                $table->id();
                $table->foreignId('mentor_id')->constrained()->cascadeOnDelete();
                $table->foreignId('mentee_id')->constrained('users')->cascadeOnDelete();
                $table->text('message');
                $table->enum('status', ['pending', 'accepted', 'rejected'])->default('pending');
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('mentor_requests');
        Schema::dropIfExists('mentors');
        Schema::dropIfExists('group_buy_participants');
        Schema::dropIfExists('group_buys');
    }
};
