<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class UserDailySpin extends Model
{
    protected $fillable = [
        'user_id', 'spun_at', 'points_awarded',
    ];

    protected $casts = [
        'spun_at' => 'date',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
