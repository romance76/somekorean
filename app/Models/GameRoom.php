<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class GameRoom extends Model
{
    use HasFactory;

    protected $fillable = [
        'game_type', 'host_id', 'status', 'max_players',
        'bet_amount', 'settings',
    ];

    protected function casts(): array
    {
        return [
            'settings' => 'array',
            'max_players' => 'integer',
            'bet_amount' => 'integer',
        ];
    }

    public function host()    { return $this->belongsTo(User::class, 'host_id'); }
    public function players() { return $this->hasMany(GamePlayer::class); }
}
