<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('board_id')->constrained()->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->longText('content');
            $table->string('thumbnail')->nullable();
            $table->json('images')->nullable();
            $table->unsignedBigInteger('view_count')->default(0);
            $table->unsignedBigInteger('like_count')->default(0);
            $table->unsignedBigInteger('comment_count')->default(0);
            $table->boolean('is_pinned')->default(false);
            $table->boolean('is_notice')->default(false);
            $table->boolean('is_anonymous')->default(false);
            $table->enum('status', ['active','hidden','deleted'])->default('active');
            $table->timestamps();
            $table->softDeletes();
            $table->index(['board_id', 'status', 'created_at']);
        });
    }
    public function down(): void { Schema::dropIfExists('posts'); }
};
