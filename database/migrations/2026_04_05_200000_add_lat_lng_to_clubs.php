<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('clubs', function (Blueprint $table) {
            $table->decimal('lat', 10, 7)->nullable()->after('zipcode');
            $table->decimal('lng', 10, 7)->nullable()->after('lat');
            $table->index(['lat', 'lng']);
        });
    }

    public function down(): void
    {
        Schema::table('clubs', function (Blueprint $table) {
            $table->dropColumn(['lat', 'lng']);
        });
    }
};
