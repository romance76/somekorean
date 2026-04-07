<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // 토너먼트 (예약/진행/완료)
        Schema::create('poker_tournaments', function (Blueprint $table) {
            $table->id();
            $table->string('title', 100); // "18:00 데일리 $500"
            $table->string('type', 20)->default('regular'); // freeroll, micro, regular, high_roller
            $table->string('status', 20)->default('scheduled'); // scheduled, registering, starting, running, finished, cancelled
            $table->integer('buy_in')->default(500);
            $table->integer('starting_chips')->default(15000);
            $table->integer('max_players')->default(90);
            $table->integer('min_players')->default(9);
            $table->timestamp('scheduled_at'); // 시작 예정 시간
            $table->timestamp('registration_opens_at')->nullable(); // 등록 오픈 시간
            $table->timestamp('started_at')->nullable(); // 실제 시작 시간
            $table->timestamp('finished_at')->nullable();
            $table->integer('late_reg_levels')->default(3); // 레이트 등록 허용 레벨
            $table->integer('blind_level')->default(0);
            $table->json('prize_pool')->nullable(); // 상금 구조
            $table->integer('bounty_pct')->default(10); // 바운티 %
            $table->timestamps();
            $table->index(['status', 'scheduled_at']);
        });

        // 토너먼트 참가자 (대기/활성/탈락)
        Schema::create('poker_tournament_entries', function (Blueprint $table) {
            $table->id();
            $table->foreignId('tournament_id')->constrained('poker_tournaments')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('status', 20)->default('registered'); // registered, seated, playing, eliminated, finished
            $table->boolean('is_online')->default(false);
            $table->timestamp('last_seen_at')->nullable();
            $table->integer('table_number')->nullable();
            $table->integer('seat_number')->nullable();
            $table->integer('chips')->default(0);
            $table->integer('finish_position')->nullable();
            $table->integer('prize_won')->default(0);
            $table->integer('bounties_earned')->default(0);
            $table->timestamp('eliminated_at')->nullable();
            $table->timestamps();
            $table->unique(['tournament_id', 'user_id']);
            $table->index(['tournament_id', 'status']);
        });

        // 토너먼트 테이블 (진행 중인 각 테이블 상태)
        Schema::create('poker_tournament_tables', function (Blueprint $table) {
            $table->id();
            $table->foreignId('tournament_id')->constrained('poker_tournaments')->cascadeOnDelete();
            $table->integer('table_number');
            $table->string('status', 20)->default('active'); // active, closed
            $table->integer('dealer_seat')->default(0);
            $table->integer('blind_level')->default(0);
            $table->json('community_cards')->nullable();
            $table->integer('pot')->default(0);
            $table->string('stage', 20)->default('waiting'); // waiting, preflop, flop, turn, river, showdown
            $table->integer('current_actor_seat')->nullable();
            $table->integer('current_bet')->default(0);
            $table->integer('hand_number')->default(0);
            $table->timestamp('action_deadline')->nullable();
            $table->json('deck')->nullable(); // 남은 덱 (암호화)
            $table->timestamps();
            $table->unique(['tournament_id', 'table_number']);
        });

        // 테이블 좌석 (각 좌석의 플레이어 상태)
        Schema::create('poker_table_seats', function (Blueprint $table) {
            $table->id();
            $table->foreignId('table_id')->constrained('poker_tournament_tables')->cascadeOnDelete();
            $table->integer('seat_number'); // 0-8
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->integer('chips')->default(0);
            $table->json('cards')->nullable(); // 홀 카드 (암호화)
            $table->boolean('is_folded')->default(false);
            $table->boolean('is_all_in')->default(false);
            $table->boolean('is_sitting_out')->default(false);
            $table->integer('current_bet')->default(0);
            $table->integer('timebank_remaining')->default(30);
            $table->timestamps();
            $table->unique(['table_id', 'seat_number']);
        });

        // 핸드 액션 로그 (서버 기록)
        Schema::create('poker_tournament_actions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('table_id')->constrained('poker_tournament_tables')->cascadeOnDelete();
            $table->integer('hand_number');
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->integer('seat_number');
            $table->string('action', 20); // fold, check, call, raise, allin, timeout, post_sb, post_bb, post_ante
            $table->integer('amount')->default(0);
            $table->string('street', 10); // preflop, flop, turn, river
            $table->timestamps();
            $table->index(['table_id', 'hand_number']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('poker_tournament_actions');
        Schema::dropIfExists('poker_table_seats');
        Schema::dropIfExists('poker_tournament_tables');
        Schema::dropIfExists('poker_tournament_entries');
        Schema::dropIfExists('poker_tournaments');
    }
};
