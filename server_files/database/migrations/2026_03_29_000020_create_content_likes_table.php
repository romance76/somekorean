<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('content_likes', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('user_id');
            $table->string('likeable_type', 100);
            $table->unsignedBigInteger('likeable_id');
            $table->timestamp('created_at')->nullable();

            $table->unique(['user_id', 'likeable_type', 'likeable_id'], 'content_likes_unique');
            $table->index(['likeable_type', 'likeable_id'], 'content_likes_item_index');
            $table->foreign('user_id')->references('id')->on('users')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('content_likes');
    }
};
