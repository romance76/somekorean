<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerGamePlayer extends Model
{
    protected $fillable = [
        'game_id', 'seat_index', 'player_type', 'player_name',
        'ai_profile', 'starting_chips', 'final_chips',
        'status', 'eliminated_at_hand',
    ];

    protected function casts(): array
    {
        return [
            'seat_index' => 'integer',
            'starting_chips' => 'integer',
            'final_chips' => 'integer',
            'eliminated_at_hand' => 'integer',
        ];
    }

    public function game()
    {
        return $this->belongsTo(PokerGame::class, 'game_id');
    }
}
