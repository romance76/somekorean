<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ElderCheckinLog extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'checked_in_at', 'lat', 'lng', 'status',
    ];

    protected function casts(): array
    {
        return [
            'checked_in_at' => 'datetime',
            'lat' => 'decimal:7',
            'lng' => 'decimal:7',
        ];
    }

    public function user() { return $this->belongsTo(User::class); }
}
