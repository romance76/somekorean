<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('market_items', function (Blueprint $t) {
            if (!Schema::hasColumn('market_items', 'zipcode')) {
                $t->string('zipcode', 10)->nullable()->after('state');
            }
        });
    }

    public function down(): void
    {
        Schema::table('market_items', function (Blueprint $t) {
            if (Schema::hasColumn('market_items', 'zipcode')) $t->dropColumn('zipcode');
        });
    }
};
