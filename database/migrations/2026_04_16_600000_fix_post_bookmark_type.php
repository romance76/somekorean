<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        // 기존 'post' → 'App\Models\Post' 통일
        DB::table('bookmarks')
            ->where('bookmarkable_type', 'post')
            ->update(['bookmarkable_type' => 'App\\Models\\Post']);
    }

    public function down(): void
    {
        DB::table('bookmarks')
            ->where('bookmarkable_type', 'App\\Models\\Post')
            ->update(['bookmarkable_type' => 'post']);
    }
};
