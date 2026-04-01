<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ElderSosLog extends Model
{
    protected $fillable = [
        'user_id', 'lat', 'lng', 'status',
        'guardian_notified', 'resolved_at', 'resolved_by', 'note',
    ];

    protected $casts = [
        'lat'                => 'decimal:7',
        'lng'                => 'decimal:7',
        'guardian_notified'  => 'boolean',
        'resolved_at'       => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function resolver()
    {
        return $this->belongsTo(User::class, 'resolved_by');
    }
}
