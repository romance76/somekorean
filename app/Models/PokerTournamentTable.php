<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerTournamentTable extends Model
{
    protected $fillable = [
        'tournament_id', 'table_number', 'status', 'dealer_seat',
        'blind_level', 'community_cards', 'pot', 'stage',
        'current_actor_seat', 'current_bet', 'hand_number',
        'action_deadline', 'deck',
    ];

    protected function casts(): array
    {
        return [
            'community_cards' => 'array',
            'deck' => 'array',
            'action_deadline' => 'datetime',
            'pot' => 'integer',
            'current_bet' => 'integer',
            'hand_number' => 'integer',
        ];
    }

    public function tournament() { return $this->belongsTo(PokerTournament::class, 'tournament_id'); }
    public function seats() { return $this->hasMany(PokerTableSeat::class, 'table_id'); }
    public function actions() { return $this->hasMany(PokerTournamentAction::class, 'table_id'); }

    public function activeSeatCount() { return $this->seats()->whereNotNull('user_id')->where('is_sitting_out', false)->count(); }
}
