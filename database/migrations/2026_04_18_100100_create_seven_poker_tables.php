<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('seven_poker_rooms', function (Blueprint $table) {
            $table->id();
            $table->string('name', 60);
            $table->foreignId('host_id')->constrained('users')->cascadeOnDelete();
            $table->integer('min_bet')->default(10000);
            $table->integer('max_seats')->default(6);
            $table->integer('buy_in')->default(1000000);
            $table->string('status', 20)->default('waiting'); // waiting, playing, ended
            $table->json('settings')->nullable();
            $table->timestamps();
            $table->index('status');
        });

        Schema::create('seven_poker_games', function (Blueprint $table) {
            $table->id();
            $table->foreignId('room_id')->constrained('seven_poker_rooms')->cascadeOnDelete();
            $table->string('status', 20)->default('dealing'); // dealing, round1-4, showdown, ended
            $table->bigInteger('pot')->default(0);
            $table->integer('current_round')->default(1);
            $table->integer('dealer_seat')->nullable();
            $table->integer('current_turn_seat')->nullable();
            $table->bigInteger('current_bet')->default(0);
            $table->json('deck')->nullable(); // 남은 카드
            $table->json('community')->nullable(); // 공개 카드(족보 판정에 영향 없음, 뻥 시)
            $table->timestamp('started_at')->nullable();
            $table->timestamp('ended_at')->nullable();
            $table->foreignId('winner_seat')->nullable();
            $table->timestamps();
        });

        Schema::create('seven_poker_seats', function (Blueprint $table) {
            $table->id();
            $table->foreignId('room_id')->constrained('seven_poker_rooms')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained('users')->cascadeOnDelete();
            $table->integer('seat_number'); // 1-6
            $table->bigInteger('stack')->default(0); // 현재 보유 칩
            $table->json('cards')->nullable(); // 7장 (공개 여부는 인덱스별 flag)
            $table->json('card_visibility')->nullable(); // [false,false,true,true,true,true,false]
            $table->bigInteger('current_bet')->default(0);
            $table->bigInteger('round_bet')->default(0);
            $table->string('state', 20)->default('active'); // active, folded, allin, out
            $table->timestamp('joined_at')->nullable();
            $table->timestamps();
            $table->unique(['room_id', 'seat_number']);
            $table->unique(['room_id', 'user_id']);
        });

        Schema::create('seven_poker_actions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('game_id')->constrained('seven_poker_games')->cascadeOnDelete();
            $table->foreignId('seat_id')->constrained('seven_poker_seats')->cascadeOnDelete();
            $table->integer('round');
            $table->string('action', 20); // fold(다이)/check/call/half/quarter/bbing(뻥)/ttadang(따당)/allin
            $table->bigInteger('amount')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('seven_poker_actions');
        Schema::dropIfExists('seven_poker_seats');
        Schema::dropIfExists('seven_poker_games');
        Schema::dropIfExists('seven_poker_rooms');
    }
};
