<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('poker_wallets', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->unique()->constrained()->cascadeOnDelete();
            $table->bigInteger('chips_balance')->default(0);
            $table->bigInteger('total_deposited')->default(0);
            $table->bigInteger('total_withdrawn')->default(0);
            $table->timestamps();
        });

        Schema::create('poker_transactions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('type', 20); // deposit, withdraw, buy_in, prize, bounty, refund
            $table->bigInteger('amount');
            $table->bigInteger('balance_after');
            $table->string('reference_type', 50)->nullable();
            $table->unsignedBigInteger('reference_id')->nullable();
            $table->string('description')->nullable();
            $table->timestamps();
            $table->index(['user_id', 'created_at']);
        });

        Schema::create('poker_games', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('type', 20)->default('solo');
            $table->string('status', 20)->default('setup'); // setup, playing, completed, abandoned
            $table->json('config')->nullable(); // {buyIn, totalPlayers, startChips}
            $table->tinyInteger('blind_level')->default(0);
            $table->integer('hands_played')->default(0);
            $table->integer('final_place')->nullable();
            $table->bigInteger('prize_won')->default(0);
            $table->integer('bounties_earned')->default(0);
            $table->bigInteger('bounty_amount')->default(0);
            $table->integer('elapsed_seconds')->default(0);
            $table->timestamps();
            $table->index(['user_id', 'status']);
        });

        Schema::create('poker_game_players', function (Blueprint $table) {
            $table->id();
            $table->foreignId('game_id')->constrained('poker_games')->cascadeOnDelete();
            $table->tinyInteger('seat_index');
            $table->string('player_type', 20); // human, ai
            $table->string('player_name', 50);
            $table->string('ai_profile', 30)->nullable();
            $table->bigInteger('starting_chips');
            $table->bigInteger('final_chips')->default(0);
            $table->string('status', 20)->default('playing'); // playing, eliminated, winner
            $table->integer('eliminated_at_hand')->nullable();
            $table->timestamps();
        });

        Schema::create('poker_hands', function (Blueprint $table) {
            $table->id();
            $table->foreignId('game_id')->constrained('poker_games')->cascadeOnDelete();
            $table->integer('hand_number');
            $table->tinyInteger('blind_level');
            $table->json('community_cards')->nullable();
            $table->bigInteger('pot_total')->default(0);
            $table->tinyInteger('winner_seat')->nullable();
            $table->string('winner_hand_name', 50)->nullable();
            $table->timestamps();
        });

        Schema::create('poker_hand_actions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('hand_id')->constrained('poker_hands')->cascadeOnDelete();
            $table->tinyInteger('seat_index');
            $table->string('action', 20); // fold, check, call, raise, allin
            $table->bigInteger('amount')->default(0);
            $table->string('street', 10); // preflop, flop, turn, river
            $table->tinyInteger('action_order');
            $table->timestamps();
        });

        Schema::create('poker_stats', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->unique()->constrained()->cascadeOnDelete();
            $table->integer('games_played')->default(0);
            $table->integer('hands_played')->default(0);
            $table->integer('tournaments_won')->default(0);
            $table->integer('in_the_money')->default(0);
            $table->integer('best_place')->nullable();
            $table->bigInteger('total_prize_won')->default(0);
            $table->integer('total_bounties')->default(0);
            $table->bigInteger('total_buy_ins')->default(0);
            $table->bigInteger('biggest_pot_won')->default(0);
            $table->string('best_hand_name', 50)->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('poker_hand_actions');
        Schema::dropIfExists('poker_hands');
        Schema::dropIfExists('poker_game_players');
        Schema::dropIfExists('poker_games');
        Schema::dropIfExists('poker_transactions');
        Schema::dropIfExists('poker_stats');
        Schema::dropIfExists('poker_wallets');
    }
};
