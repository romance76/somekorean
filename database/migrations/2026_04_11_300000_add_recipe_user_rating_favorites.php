<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // recipe_posts 확장: 유저 업로드 / 한영 / 평점 집계
        Schema::table('recipe_posts', function (Blueprint $table) {
            if (!Schema::hasColumn('recipe_posts', 'user_id')) {
                $table->unsignedBigInteger('user_id')->nullable()->after('id');
                $table->index('user_id');
            }
            if (!Schema::hasColumn('recipe_posts', 'title_en')) {
                $table->string('title_en', 200)->nullable()->after('title');
            }
            if (!Schema::hasColumn('recipe_posts', 'ingredients_en')) {
                $table->text('ingredients_en')->nullable()->after('ingredients');
            }
            if (!Schema::hasColumn('recipe_posts', 'servings')) {
                $table->string('servings', 50)->nullable()->after('ingredients_en');
            }
            if (!Schema::hasColumn('recipe_posts', 'rating_avg')) {
                $table->decimal('rating_avg', 3, 2)->default(0)->after('like_count');
            }
            if (!Schema::hasColumn('recipe_posts', 'rating_count')) {
                $table->integer('rating_count')->default(0)->after('rating_avg');
            }
            if (!Schema::hasColumn('recipe_posts', 'favorite_count')) {
                $table->integer('favorite_count')->default(0)->after('rating_count');
            }
        });

        // 찜 (favorites)
        Schema::create('recipe_favorites', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('recipe_id')->constrained('recipe_posts')->cascadeOnDelete();
            $table->timestamps();
            $table->unique(['user_id', 'recipe_id']);
        });

        // 평점 (ratings)
        Schema::create('recipe_ratings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('recipe_id')->constrained('recipe_posts')->cascadeOnDelete();
            $table->tinyInteger('rating'); // 1-5
            $table->text('comment')->nullable();
            $table->timestamps();
            $table->unique(['user_id', 'recipe_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('recipe_ratings');
        Schema::dropIfExists('recipe_favorites');
        Schema::table('recipe_posts', function (Blueprint $table) {
            $table->dropColumn([
                'user_id', 'title_en', 'ingredients_en', 'servings',
                'rating_avg', 'rating_count', 'favorite_count',
            ]);
        });
    }
};
