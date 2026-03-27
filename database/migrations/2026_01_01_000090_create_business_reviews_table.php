<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('business_reviews', function (Blueprint $table) {
            $table->id();
            $table->foreignId('business_id')->constrained()->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->unsignedTinyInteger('rating');
            $table->text('content')->nullable();
            $table->json('photos')->nullable();
            $table->timestamps();
            $table->unique(['business_id', 'user_id']);
        });
    }
    public function down(): void { Schema::dropIfExists('business_reviews'); }
};
