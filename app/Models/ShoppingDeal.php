<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ShoppingDeal extends Model
{
    use HasFactory;

    protected $fillable = [
        'store_id', 'title', 'description', 'image_url',
        'original_price', 'sale_price', 'discount_percent',
        'url', 'is_active', 'expires_at',
    ];

    protected function casts(): array
    {
        return [
            'original_price' => 'decimal:2',
            'sale_price' => 'decimal:2',
            'discount_percent' => 'integer',
            'is_active' => 'boolean',
            'expires_at' => 'datetime',
        ];
    }

    public function store() { return $this->belongsTo(ShoppingStore::class, 'store_id'); }
}
