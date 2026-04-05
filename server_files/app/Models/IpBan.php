<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class IpBan extends Model
{
    protected $fillable = [
        'ip_address', 'cidr_range', 'fingerprint_hash',
        'reason', 'banned_by', 'expires_at',
    ];

    protected $casts = [
        'expires_at' => 'datetime',
    ];

    public function bannedByUser()
    {
        return $this->belongsTo(User::class, 'banned_by');
    }

    /**
     * 활성 밴 (영구 또는 만료 전)
     */
    public function scopeActive($query)
    {
        return $query->where(function ($q) {
            $q->whereNull('expires_at')
              ->orWhere('expires_at', '>', now());
        });
    }
}
