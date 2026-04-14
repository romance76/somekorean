<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('qa_answer_likes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('qa_answer_id')->constrained('qa_answers')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->timestamp('created_at')->nullable();
            $table->unique(['qa_answer_id', 'user_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('qa_answer_likes');
    }
};
