<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MarketReservation extends Model
{
    protected $fillable = [
        'market_item_id', 'buyer_id', 'seller_id',
        'points_held', 'expires_at', 'status',
        'completed_at', 'cancelled_at',
    ];

    protected $casts = [
        'expires_at' => 'datetime',
        'completed_at' => 'datetime',
        'cancelled_at' => 'datetime',
    ];

    public function marketItem()
    {
        return $this->belongsTo(MarketItem::class);
    }

    public function buyer()
    {
        return $this->belongsTo(User::class, 'buyer_id');
    }

    public function seller()
    {
        return $this->belongsTo(User::class, 'seller_id');
    }

    public function scopePending($query)
    {
        return $query->where('status', 'pending');
    }

    public function scopeExpired($query)
    {
        return $query->where('status', 'pending')
                     ->where('expires_at', '<', now());
    }
}
