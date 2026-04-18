<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class SevenPokerGame extends Model
{
    protected $fillable = [
        'room_id','status','pot','current_round','dealer_seat','current_turn_seat',
        'current_bet','deck','community','started_at','ended_at','winner_seat',
    ];
    protected $casts = [
        'deck' => 'array', 'community' => 'array',
        'pot' => 'integer', 'current_bet' => 'integer',
        'started_at' => 'datetime', 'ended_at' => 'datetime',
    ];

    public function room() { return $this->belongsTo(SevenPokerRoom::class, 'room_id'); }
    public function actions() { return $this->hasMany(SevenPokerAction::class, 'game_id'); }
}
