<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Payment extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'stripe_payment_id', 'amount', 'currency',
        'points_purchased', 'status',
    ];

    protected function casts(): array
    {
        return [
            'amount' => 'decimal:2',
            'points_purchased' => 'integer',
        ];
    }

    public function user() { return $this->belongsTo(User::class); }
}
