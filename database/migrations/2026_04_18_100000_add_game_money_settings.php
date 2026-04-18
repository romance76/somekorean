<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    public function up(): void
    {
        $defaults = [
            ['key' => 'game_money.enabled',          'value' => '1',     'label' => '게임머니 환전 활성화', 'category' => 'game_money'],
            ['key' => 'game_money.rate_to_game',     'value' => '10000', 'label' => '1 포인트당 게임머니',   'category' => 'game_money'],
            ['key' => 'game_money.withdraw_fee_pct', 'value' => '10',    'label' => '역환전 수수료 %',       'category' => 'game_money'],
            ['key' => 'game_money.min_exchange_p',   'value' => '10',    'label' => '최소 환전 포인트',       'category' => 'game_money'],
            ['key' => 'game_money.min_withdraw_gm',  'value' => '100000','label' => '최소 역환전 게임머니',    'category' => 'game_money'],
        ];

        foreach ($defaults as $d) {
            DB::table('point_settings')->updateOrInsert(
                ['key' => $d['key']],
                array_merge($d, ['created_at' => now(), 'updated_at' => now()])
            );
        }
    }

    public function down(): void
    {
        DB::table('point_settings')->where('key', 'like', 'game_money.%')->delete();
    }
};
