<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('checkins', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->date('checkin_date')->unique();
            $table->unsignedInteger('streak_days')->default(1);
            $table->timestamp('created_at')->useCurrent();
        });
        Schema::table('checkins', function (Blueprint $table) {
            $table->dropUnique(['checkin_date']);
            $table->unique(['user_id', 'checkin_date']);
        });
    }
    public function down(): void { Schema::dropIfExists('checkins'); }
};
