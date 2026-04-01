<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('recipe_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 50);
            $table->string('key', 30)->unique();
            $table->string('icon', 10)->nullable();
            $table->integer('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('recipe_posts', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('category_id');
            $table->unsignedBigInteger('user_id');
            $table->string('title', 200);
            $table->text('intro')->nullable();
            $table->string('difficulty', 10)->default('보통'); // 쉬움, 보통, 어려움
            $table->string('cook_time', 30)->nullable(); // "30분", "1시간"
            $table->unsignedInteger('calories')->nullable();
            $table->integer('servings')->default(2);
            $table->json('ingredients')->nullable();
            $table->json('steps')->nullable();
            $table->json('tips')->nullable();
            $table->json('tags')->nullable();
            $table->string('image_url', 500)->nullable();
            $table->string('image_credit', 300)->nullable();
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('like_count')->default(0);
            $table->unsignedInteger('bookmark_count')->default(0);
            $table->string('source', 20)->default('user'); // user, ai
            $table->boolean('is_hidden')->default(false);
            $table->timestamps();
            $table->foreign('category_id')->references('id')->on('recipe_categories');
            $table->foreign('user_id')->references('id')->on('users');
        });

        Schema::create('recipe_comments', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('recipe_id');
            $table->unsignedBigInteger('user_id');
            $table->text('content');
            $table->unsignedInteger('rating')->nullable(); // 1-5
            $table->timestamps();
            $table->foreign('recipe_id')->references('id')->on('recipe_posts')->onDelete('cascade');
            $table->foreign('user_id')->references('id')->on('users');
        });
    }

    public function down(): void {
        Schema::dropIfExists('recipe_comments');
        Schema::dropIfExists('recipe_posts');
        Schema::dropIfExists('recipe_categories');
    }
};
