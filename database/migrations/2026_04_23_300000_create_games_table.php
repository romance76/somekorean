<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('games', function (Blueprint $table) {
            $table->id();
            $table->string('slug', 50)->unique();       // 라우트용 (gostop, poker, ...)
            $table->string('name', 100);
            $table->string('description', 200)->nullable();
            $table->string('icon', 20)->default('🎮');
            $table->string('category', 30)->default('brain'); // card/brain/arcade/word/education
            $table->string('path', 200);                 // 프론트 라우트 경로 (/games/gostop)
            $table->boolean('is_active')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
            $table->index(['is_active','category','sort_order']);
        });

        // 초기 데이터 시드
        $games = [
            ['gostop',       '고스톱',         '한국 전통 카드',   '🎴', 'card',      '/games/gostop'],
            ['poker',        '토너먼트 포커',  'AI 대전 토너먼트', '♠️', 'card',      '/games/poker'],
            ['holdem',       '홀덤',           '1인 홀덤',         '♦️', 'card',      '/games/holdem'],
            ['blackjack',    '블랙잭',         '21 카드',          '🂡', 'card',      '/games/blackjack'],
            ['memory',       '메모리',         '카드 짝맞추기',    '🧩', 'brain',     '/games/memory'],
            ['2048',         '2048',           '숫자 퍼즐',        '🔢', 'brain',     '/games/2048'],
            ['omok',         '오목',           '5목',              '⚫', 'brain',     '/games/omok'],
            ['puzzle',       '퍼즐',           '조각 맞추기',      '🧩', 'brain',     '/games/puzzle'],
            ['bingo',        '빙고',           '빙고 게임',        '📋', 'brain',     '/games/bingo'],
            ['speedcalc',    '빠른계산',       '암산 훈련',        '➕', 'brain',     '/games/speedcalc'],
            ['seniormemory', '시니어 기억력',  '기억력 훈련',      '🧠', 'brain',     '/games/seniormemory'],
            ['snake',        '스네이크',       '뱀 키우기',        '🐍', 'arcade',    '/games/snake'],
            ['towerdefense', '타워 디펜스',    '타워 방어',        '🏰', 'arcade',    '/games/towerdefense'],
            ['slots',        '슬롯머신',       '행운의 슬롯',      '🎰', 'arcade',    '/games/slots'],
            ['stocksim',     '주식 시뮬',      '모의 투자',        '📈', 'arcade',    '/games/stocksim'],
            ['wordle',       '워들',           '5글자 단어',       '🔤', 'word',      '/games/wordle'],
            ['quiz',         '퀴즈',           '일반 상식',        '❓', 'word',      '/games/quiz'],
            ['wordchain',    '끝말잇기',       '단어 이어가기',    '🔗', 'word',      '/games/wordchain'],
            ['wordblank',    '빈칸채우기',     '단어 완성',        '📝', 'word',      '/games/wordblank'],
            ['spelling',     '스펠링',         '영단어',           '📖', 'word',      '/games/spelling'],
            ['typing',       '타이핑',         '타자 연습',        '⌨️', 'word',      '/games/typing'],
            ['hangul',       '한글',           '한글 학습',        '🇰🇷', 'education', '/games/hangul'],
            ['counting',     '수세기',         '유아 수학',        '🔢', 'education', '/games/counting'],
            ['colors',       '색깔',           '색상 학습',        '🎨', 'education', '/games/colors'],
            ['shapes',       '도형',           '도형 학습',        '🔷', 'education', '/games/shapes'],
            ['satwords',     'SAT 단어',       'SAT 준비',         '📚', 'education', '/games/satwords'],
            ['proverb',      '속담 퀴즈',      '한국 속담',        '📜', 'education', '/games/proverb'],
            ['flag',         '국기 퀴즈',      '세계 국기',        '🏳️', 'education', '/games/flag'],
            ['uslife',       '미국 생활',      '시민권 퀴즈',      '🇺🇸', 'education', '/games/uslife'],
        ];
        $now = now();
        $rows = [];
        foreach ($games as $i => $g) {
            $rows[] = [
                'slug'        => $g[0],
                'name'        => $g[1],
                'description' => $g[2],
                'icon'        => $g[3],
                'category'    => $g[4],
                'path'        => $g[5],
                'is_active'   => true,
                'sort_order'  => $i,
                'created_at'  => $now,
                'updated_at'  => $now,
            ];
        }
        DB::table('games')->insert($rows);
    }

    public function down(): void
    {
        Schema::dropIfExists('games');
    }
};
