<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class SevenPokerSeat extends Model
{
    protected $fillable = [
        'room_id','user_id','seat_number','stack','cards','card_visibility',
        'current_bet','round_bet','state','joined_at',
    ];
    protected $casts = [
        'cards' => 'array', 'card_visibility' => 'array',
        'stack' => 'integer', 'current_bet' => 'integer', 'round_bet' => 'integer',
        'joined_at' => 'datetime',
    ];

    public function user() { return $this->belongsTo(User::class); }
    public function room() { return $this->belongsTo(SevenPokerRoom::class, 'room_id'); }
}
