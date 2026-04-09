<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('comments', function (Blueprint $table) {
            if (!Schema::hasColumn('comments', 'parent_id')) {
                $table->unsignedBigInteger('parent_id')->nullable()->after('content');
            }
            if (!Schema::hasColumn('comments', 'likes')) {
                $table->integer('likes')->default(0)->after('parent_id');
            }
            if (!Schema::hasColumn('comments', 'dislikes')) {
                $table->integer('dislikes')->default(0)->after('likes');
            }
        });

        if (!Schema::hasTable('comment_votes')) {
            Schema::create('comment_votes', function (Blueprint $table) {
                $table->id();
                $table->foreignId('comment_id')->constrained()->cascadeOnDelete();
                $table->foreignId('user_id')->constrained()->cascadeOnDelete();
                $table->enum('vote', ['like', 'dislike']);
                $table->timestamps();
                $table->unique(['comment_id', 'user_id']);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('comment_votes');
        Schema::table('comments', function (Blueprint $table) {
            $table->dropColumn(['parent_id', 'likes', 'dislikes']);
        });
    }
};
