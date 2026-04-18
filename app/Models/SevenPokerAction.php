<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class SevenPokerAction extends Model
{
    protected $fillable = ['game_id', 'seat_id', 'round', 'action', 'amount'];
    protected $casts = ['amount' => 'integer'];
}
