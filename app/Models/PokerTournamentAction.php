<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerTournamentAction extends Model
{
    protected $fillable = [
        'table_id', 'hand_number', 'user_id', 'seat_number',
        'action', 'amount', 'street',
    ];

    protected function casts(): array
    {
        return ['amount' => 'integer'];
    }

    public function table() { return $this->belongsTo(PokerTournamentTable::class, 'table_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
