<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class SevenPokerRoom extends Model
{
    protected $fillable = ['name', 'host_id', 'min_bet', 'max_seats', 'buy_in', 'status', 'settings'];
    protected $casts = ['settings' => 'array', 'min_bet' => 'integer', 'max_seats' => 'integer', 'buy_in' => 'integer'];

    public function host() { return $this->belongsTo(User::class, 'host_id'); }
    public function seats() { return $this->hasMany(SevenPokerSeat::class, 'room_id'); }
    public function currentGame() { return $this->hasOne(SevenPokerGame::class, 'room_id')->latestOfMany(); }
}
