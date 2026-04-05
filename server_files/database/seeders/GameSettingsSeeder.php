<?php

namespace Database\Seeders;

use App\Models\GameSetting;
use Illuminate\Database\Seeder;

class GameSettingsSeeder extends Seeder
{
    public function run(): void
    {
        $settings = [
            [
                'key' => 'daily_login_coins',
                'value' => '50',
                'description' => '일일 로그인 보상 코인',
            ],
            [
                'key' => 'coin_to_game_money_rate',
                'value' => '50',
                'description' => '코인 → 게임머니 변환 비율',
            ],
            [
                'key' => 'spin_min',
                'value' => '0',
                'description' => '룰렛 최소 보상',
            ],
            [
                'key' => 'spin_max',
                'value' => '100',
                'description' => '룰렛 최대 보상',
            ],
            [
                'key' => 'spin_jackpot_max',
                'value' => '300',
                'description' => '룰렛 잭팟 최대 보상',
            ],
            [
                'key' => 'spin_jackpot_chance',
                'value' => '5',
                'description' => '룰렛 잭팟 확률 (%)',
            ],
            [
                'key' => 'normal_game_reward_multiplier',
                'value' => '0.01',
                'description' => '일반 게임 보상 배수',
            ],
            [
                'key' => 'betting_game_types',
                'value' => 'go_stop,holdem,blackjack',
                'description' => '배팅 가능 게임 종류',
            ],
        ];

        foreach ($settings as $setting) {
            GameSetting::updateOrCreate(
                ['key' => $setting['key']],
                $setting
            );
        }
    }
}
