<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('market_items', function (Blueprint $table) {
            $table->integer('reservation_points')->default(0)->after('status');
            $table->integer('reservation_hours')->default(24)->after('reservation_points');
        });
    }

    public function down(): void
    {
        Schema::table('market_items', function (Blueprint $table) {
            $table->dropColumn(['reservation_points', 'reservation_hours']);
        });
    }
};
