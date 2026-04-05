<?php

namespace Database\Seeders;

use App\Models\GameSetting;
use Illuminate\Database\Seeder;

class GameSettingSeeder extends Seeder
{
    public function run(): void
    {
        $settings = [
            // 오목 (Omok / Gomoku)
            ['game_type' => 'omok',     'key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'omok',     'key' => 'board_size',   'value' => '15'],
            ['game_type' => 'omok',     'key' => 'time_limit',   'value' => '30'],
            ['game_type' => 'omok',     'key' => 'min_bet',      'value' => '0'],
            ['game_type' => 'omok',     'key' => 'max_bet',      'value' => '500'],
            ['game_type' => 'omok',     'key' => 'win_points',   'value' => '50'],

            // 고스톱 (GoStop)
            ['game_type' => 'gostop',   'key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'gostop',   'key' => 'max_players',  'value' => '3'],
            ['game_type' => 'gostop',   'key' => 'min_bet',      'value' => '10'],
            ['game_type' => 'gostop',   'key' => 'max_bet',      'value' => '1000'],
            ['game_type' => 'gostop',   'key' => 'base_points',  'value' => '100'],
            ['game_type' => 'gostop',   'key' => 'go_multiplier','value' => '2'],

            // 포커 (Poker / Texas Holdem)
            ['game_type' => 'holdem',   'key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'holdem',   'key' => 'max_players',  'value' => '6'],
            ['game_type' => 'holdem',   'key' => 'min_bet',      'value' => '10'],
            ['game_type' => 'holdem',   'key' => 'max_bet',      'value' => '5000'],
            ['game_type' => 'holdem',   'key' => 'blind_small',  'value' => '5'],
            ['game_type' => 'holdem',   'key' => 'blind_big',    'value' => '10'],

            // 블랙잭 (Blackjack)
            ['game_type' => 'blackjack','key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'blackjack','key' => 'max_players',  'value' => '5'],
            ['game_type' => 'blackjack','key' => 'min_bet',      'value' => '10'],
            ['game_type' => 'blackjack','key' => 'max_bet',      'value' => '2000'],
            ['game_type' => 'blackjack','key' => 'decks',        'value' => '6'],

            // 2048
            ['game_type' => '2048',     'key' => 'enabled',      'value' => 'true'],
            ['game_type' => '2048',     'key' => 'win_score',    'value' => '2048'],
            ['game_type' => '2048',     'key' => 'points_per_win','value' => '30'],

            // 빙고 (Bingo)
            ['game_type' => 'bingo',    'key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'bingo',    'key' => 'grid_size',    'value' => '5'],
            ['game_type' => 'bingo',    'key' => 'max_players',  'value' => '10'],
            ['game_type' => 'bingo',    'key' => 'win_points',   'value' => '20'],

            // 메모리 (Memory Match)
            ['game_type' => 'memory',   'key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'memory',   'key' => 'grid_size',    'value' => '4'],
            ['game_type' => 'memory',   'key' => 'time_limit',   'value' => '120'],
            ['game_type' => 'memory',   'key' => 'points_per_win','value' => '15'],

            // 퀴즈 (Quiz)
            ['game_type' => 'quiz',     'key' => 'enabled',      'value' => 'true'],
            ['game_type' => 'quiz',     'key' => 'questions_per_game', 'value' => '10'],
            ['game_type' => 'quiz',     'key' => 'time_per_question',  'value' => '30'],
            ['game_type' => 'quiz',     'key' => 'points_per_correct', 'value' => '10'],

            // 글로벌 게임 설정
            ['game_type' => 'global',   'key' => 'daily_free_points',    'value' => '100'],
            ['game_type' => 'global',   'key' => 'daily_spin_enabled',   'value' => 'true'],
            ['game_type' => 'global',   'key' => 'spin_min_reward',      'value' => '5'],
            ['game_type' => 'global',   'key' => 'spin_max_reward',      'value' => '500'],
            ['game_type' => 'global',   'key' => 'leaderboard_enabled',  'value' => 'true'],
            ['game_type' => 'global',   'key' => 'point_shop_enabled',   'value' => 'true'],
        ];

        foreach ($settings as $setting) {
            GameSetting::updateOrCreate(
                ['game_type' => $setting['game_type'], 'key' => $setting['key']],
                ['value' => $setting['value']]
            );
        }

        $this->command->info('GameSettingSeeder: ' . count($settings) . ' game settings created');
    }
}
