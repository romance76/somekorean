<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('user_daily_spins', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->date('spun_at');
            $table->integer('points_awarded');
            $table->timestamps();

            $table->unique(['user_id', 'spun_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('user_daily_spins');
    }
};
