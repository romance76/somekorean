<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('ip_bans', function (Blueprint $table) {
            $table->id();
            $table->string('ip_address', 45);
            $table->string('cidr_range', 50)->nullable();
            $table->string('fingerprint_hash', 255)->nullable();
            $table->text('reason')->nullable();
            $table->foreignId('banned_by')->nullable()->constrained('users')->onDelete('set null');
            $table->timestamp('expires_at')->nullable();
            $table->timestamps();

            $table->index('ip_address');
            $table->index('fingerprint_hash');
            $table->index('expires_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('ip_bans');
    }
};
