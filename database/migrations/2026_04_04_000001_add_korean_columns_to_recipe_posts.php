<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('recipe_posts', function (Blueprint $table) {
            $table->string('title_ko', 200)->nullable()->after('title');
            $table->text('intro_ko')->nullable()->after('intro');
            $table->json('ingredients_ko')->nullable()->after('ingredients');
            $table->json('steps_ko')->nullable()->after('steps');
            $table->json('tips_ko')->nullable()->after('tips');
        });

        Schema::table('recipe_categories', function (Blueprint $table) {
            $table->string('name_ko', 50)->nullable()->after('name');
        });
    }

    public function down(): void
    {
        Schema::table('recipe_posts', function (Blueprint $table) {
            $table->dropColumn(['title_ko', 'intro_ko', 'ingredients_ko', 'steps_ko', 'tips_ko']);
        });

        Schema::table('recipe_categories', function (Blueprint $table) {
            $table->dropColumn('name_ko');
        });
    }
};
