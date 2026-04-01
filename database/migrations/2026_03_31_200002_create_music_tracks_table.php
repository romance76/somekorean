<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('music_tracks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('category_id')->constrained('music_categories')->onDelete('cascade');
            $table->string('title');
            $table->string('artist')->nullable();
            $table->string('youtube_url');
            $table->string('youtube_id', 50);
            $table->string('thumbnail')->nullable();
            $table->integer('duration_seconds')->nullable();
            $table->integer('sort_order')->default(0);
            $table->integer('play_count')->default(0);
            $table->boolean('is_active')->default(true);
            $table->foreignId('added_by')->constrained('users')->onDelete('cascade');
            $table->timestamps();
        });
    }
    public function down(): void { Schema::dropIfExists('music_tracks'); }
};
