<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Payment extends Model
{
    protected $fillable = [
        'user_id', 'transaction_id', 'type', 'item_name',
        'amount', 'currency', 'payment_method', 'card_brand',
        'card_last4', 'status', 'stripe_payment_id', 'memo', 'paid_at',
    ];

    protected $casts = [
        'amount'  => 'decimal:2',
        'paid_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
