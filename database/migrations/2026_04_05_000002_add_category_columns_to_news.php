<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('news', function (Blueprint $table) {
            if (!Schema::hasColumn('news', 'category_id')) {
                $table->unsignedBigInteger('category_id')->nullable()->after('category');
            }
            if (!Schema::hasColumn('news', 'main_category_id')) {
                $table->unsignedBigInteger('main_category_id')->nullable()->after('category_id');
            }
            if (!Schema::hasColumn('news', 'is_featured')) {
                $table->boolean('is_featured')->default(false)->after('main_category_id');
            }
            if (!Schema::hasColumn('news', 'is_digest')) {
                $table->boolean('is_digest')->default(false)->after('is_featured');
            }
            if (!Schema::hasColumn('news', 'view_count')) {
                $table->unsignedInteger('view_count')->default(0)->after('is_digest');
            }
            if (!Schema::hasColumn('news', 'like_count')) {
                $table->unsignedInteger('like_count')->default(0)->after('view_count');
            }
        });
    }

    public function down(): void
    {
        Schema::table('news', function (Blueprint $table) {
            $columns = ['category_id', 'main_category_id', 'is_featured', 'is_digest', 'view_count', 'like_count'];
            foreach ($columns as $col) {
                if (Schema::hasColumn('news', $col)) {
                    $table->dropColumn($col);
                }
            }
        });
    }
};
