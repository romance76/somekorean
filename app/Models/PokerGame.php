<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerGame extends Model
{
    protected $fillable = [
        'user_id', 'type', 'status', 'config', 'blind_level',
        'hands_played', 'final_place', 'prize_won',
        'bounties_earned', 'bounty_amount', 'elapsed_seconds',
    ];

    protected function casts(): array
    {
        return [
            'config' => 'array',
            'blind_level' => 'integer',
            'hands_played' => 'integer',
            'final_place' => 'integer',
            'prize_won' => 'integer',
            'bounties_earned' => 'integer',
            'bounty_amount' => 'integer',
            'elapsed_seconds' => 'integer',
        ];
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function players()
    {
        return $this->hasMany(PokerGamePlayer::class, 'game_id');
    }

    public function hands()
    {
        return $this->hasMany(PokerHand::class, 'game_id');
    }
}
