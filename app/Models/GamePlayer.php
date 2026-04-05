<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class GamePlayer extends Model
{
    use HasFactory;

    protected $fillable = [
        'game_room_id', 'user_id', 'score', 'is_winner', 'bet_amount',
    ];

    protected function casts(): array
    {
        return [
            'score' => 'integer',
            'is_winner' => 'boolean',
            'bet_amount' => 'integer',
        ];
    }

    public function gameRoom() { return $this->belongsTo(GameRoom::class); }
    public function user()     { return $this->belongsTo(User::class); }
}
