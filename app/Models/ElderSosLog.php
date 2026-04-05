<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ElderSosLog extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'lat', 'lng', 'message',
        'contacts_notified', 'resolved_at',
    ];

    protected function casts(): array
    {
        return [
            'contacts_notified' => 'array',
            'resolved_at' => 'datetime',
            'lat' => 'decimal:7',
            'lng' => 'decimal:7',
        ];
    }

    public function user() { return $this->belongsTo(User::class); }
}
