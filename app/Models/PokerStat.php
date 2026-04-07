<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerStat extends Model
{
    protected $fillable = [
        'user_id', 'games_played', 'hands_played', 'tournaments_won',
        'in_the_money', 'best_place', 'total_prize_won', 'total_bounties',
        'total_buy_ins', 'biggest_pot_won', 'best_hand_name',
    ];

    protected function casts(): array
    {
        return [
            'games_played' => 'integer',
            'hands_played' => 'integer',
            'tournaments_won' => 'integer',
            'in_the_money' => 'integer',
            'best_place' => 'integer',
            'total_prize_won' => 'integer',
            'total_bounties' => 'integer',
            'total_buy_ins' => 'integer',
            'biggest_pot_won' => 'integer',
        ];
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
