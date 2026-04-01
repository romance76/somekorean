<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('qa_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 50);
            $table->string('key', 30)->unique();
            $table->string('icon', 10)->nullable();
            $table->string('color', 20)->default('blue');
            $table->integer('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('qa_posts', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('category_id');
            $table->unsignedBigInteger('user_id');
            $table->string('title', 200);
            $table->text('content');
            $table->string('region', 50)->nullable();
            $table->string('status', 20)->default('open'); // open, solved, closed
            $table->string('source', 20)->default('user'); // user, ai
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('answer_count')->default(0);
            $table->unsignedInteger('like_count')->default(0);
            $table->unsignedBigInteger('best_answer_id')->nullable();
            $table->boolean('is_pinned')->default(false);
            $table->boolean('is_hidden')->default(false);
            $table->timestamps();
            $table->foreign('category_id')->references('id')->on('qa_categories');
            $table->foreign('user_id')->references('id')->on('users');
        });

        Schema::create('qa_answers', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('qa_post_id');
            $table->unsignedBigInteger('user_id');
            $table->text('content');
            $table->boolean('is_best')->default(false);
            $table->unsignedInteger('like_count')->default(0);
            $table->string('source', 20)->default('user'); // user, ai
            $table->boolean('is_hidden')->default(false);
            $table->timestamps();
            $table->foreign('qa_post_id')->references('id')->on('qa_posts')->onDelete('cascade');
            $table->foreign('user_id')->references('id')->on('users');
        });
    }

    public function down(): void {
        Schema::dropIfExists('qa_answers');
        Schema::dropIfExists('qa_posts');
        Schema::dropIfExists('qa_categories');
    }
};
