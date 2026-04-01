<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('chat_messages', function (Blueprint $table) {
            $table->string('file_url')->nullable()->after('message');
            $table->string('file_name')->nullable()->after('file_url');
            $table->string('file_type')->nullable()->after('file_name'); // image | file
        });

        Schema::create('user_blocks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('blocked_user_id')->constrained('users')->cascadeOnDelete();
            $table->timestamps();
            $table->unique(['user_id', 'blocked_user_id']);
        });

        Schema::create('chat_reports', function (Blueprint $table) {
            $table->id();
            $table->foreignId('reporter_id')->constrained('users')->cascadeOnDelete();
            $table->foreignId('message_id')->constrained('chat_messages')->cascadeOnDelete();
            $table->string('reason')->default('spam');
            $table->timestamps();
            $table->unique(['reporter_id', 'message_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('chat_reports');
        Schema::dropIfExists('user_blocks');
        Schema::table('chat_messages', function (Blueprint $table) {
            $table->dropColumn(['file_url', 'file_name', 'file_type']);
        });
    }
};
