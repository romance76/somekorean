<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerTableSeat extends Model
{
    protected $fillable = [
        'table_id', 'seat_number', 'user_id', 'chips', 'cards',
        'is_folded', 'is_all_in', 'is_sitting_out', 'current_bet',
        'timebank_remaining',
    ];

    protected function casts(): array
    {
        return [
            'cards' => 'array',
            'chips' => 'integer',
            'current_bet' => 'integer',
            'timebank_remaining' => 'integer',
            'is_folded' => 'boolean',
            'is_all_in' => 'boolean',
            'is_sitting_out' => 'boolean',
        ];
    }

    public function table() { return $this->belongsTo(PokerTournamentTable::class, 'table_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
