<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MarketReservation extends Model
{
    use HasFactory;

    protected $fillable = [
        'market_item_id', 'buyer_id', 'seller_id',
        'points_held', 'status', 'completed_at', 'cancelled_at',
    ];

    protected function casts(): array
    {
        return [
            'points_held' => 'integer',
            'completed_at' => 'datetime',
            'cancelled_at' => 'datetime',
        ];
    }

    public function marketItem() { return $this->belongsTo(MarketItem::class); }
    public function buyer()      { return $this->belongsTo(User::class, 'buyer_id'); }
    public function seller()     { return $this->belongsTo(User::class, 'seller_id'); }
}
