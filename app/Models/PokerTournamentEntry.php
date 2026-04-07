<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerTournamentEntry extends Model
{
    protected $fillable = [
        'tournament_id', 'user_id', 'status', 'is_online', 'last_seen_at',
        'table_number', 'seat_number', 'chips', 'finish_position',
        'prize_won', 'bounties_earned', 'eliminated_at',
    ];

    protected function casts(): array
    {
        return [
            'is_online' => 'boolean',
            'last_seen_at' => 'datetime',
            'eliminated_at' => 'datetime',
            'chips' => 'integer',
            'finish_position' => 'integer',
            'prize_won' => 'integer',
            'bounties_earned' => 'integer',
        ];
    }

    public function tournament() { return $this->belongsTo(PokerTournament::class, 'tournament_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
