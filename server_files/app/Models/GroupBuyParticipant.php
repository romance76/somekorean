<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GroupBuyParticipant extends Model
{
    protected $fillable = ['group_buy_id', 'user_id', 'quantity'];

    public function user()     { return $this->belongsTo(User::class); }
    public function groupBuy() { return $this->belongsTo(GroupBuy::class); }
}
