<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('clubs', function (Blueprint $table) {
            $table->boolean('is_online')->default(false)->after('member_count');
            $table->string('zip_code', 10)->nullable()->after('is_online');
        });
    }

    public function down(): void
    {
        Schema::table('clubs', function (Blueprint $table) {
            $table->dropColumn(['is_online', 'zip_code']);
        });
    }
};
