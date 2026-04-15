<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('market_items', function (Blueprint $table) {
            if (!Schema::hasColumn('market_items', 'thumbnail_index')) {
                $table->unsignedTinyInteger('thumbnail_index')->default(0)->after('images');
            }
        });
    }

    public function down(): void
    {
        Schema::table('market_items', function (Blueprint $table) {
            if (Schema::hasColumn('market_items', 'thumbnail_index')) {
                $table->dropColumn('thumbnail_index');
            }
        });
    }
};
