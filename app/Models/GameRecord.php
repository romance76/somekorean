<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GameRecord extends Model
{
    protected $fillable = ['user_id', 'game_slug', 'level', 'time_ms', 'score'];

    protected $casts = [
        'level'   => 'int',
        'time_ms' => 'int',
        'score'   => 'int',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
