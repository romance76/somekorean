<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('game_records', function (Blueprint $t) {
            $t->id();
            $t->foreignId('user_id')->constrained()->cascadeOnDelete();
            $t->string('game_slug', 50)->index();   // 'flag', 'sat_words', 'proverb' ...
            $t->unsignedTinyInteger('level');       // 1~5
            $t->unsignedInteger('time_ms');         // 레벨 클리어 소요 시간 (ms)
            $t->unsignedInteger('score')->default(0);
            $t->timestamps();

            // 유저당 게임+레벨 조합은 유일 — 갱신 방식
            $t->unique(['user_id', 'game_slug', 'level']);
            // 리더보드 쿼리 최적화
            $t->index(['game_slug', 'level', 'time_ms']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('game_records');
    }
};
