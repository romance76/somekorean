<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserDailySpin extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'spun_at', 'points_won',
    ];

    protected function casts(): array
    {
        return [
            'spun_at' => 'datetime',
            'points_won' => 'integer',
        ];
    }

    public function user() { return $this->belongsTo(User::class); }
}
