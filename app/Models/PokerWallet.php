<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerWallet extends Model
{
    protected $fillable = ['user_id', 'chips_balance', 'total_deposited', 'total_withdrawn'];

    protected function casts(): array
    {
        return [
            'chips_balance' => 'integer',
            'total_deposited' => 'integer',
            'total_withdrawn' => 'integer',
        ];
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function transactions()
    {
        return $this->hasMany(PokerTransaction::class, 'user_id', 'user_id');
    }

    public function deposit(int $amount, string $description = '포인트 전환'): PokerTransaction
    {
        $this->increment('chips_balance', $amount);
        $this->increment('total_deposited', $amount);

        return PokerTransaction::create([
            'user_id' => $this->user_id,
            'type' => 'deposit',
            'amount' => $amount,
            'balance_after' => $this->fresh()->chips_balance,
            'description' => $description,
        ]);
    }

    public function withdraw(int $amount, string $description = '포인트 전환'): PokerTransaction
    {
        $this->decrement('chips_balance', $amount);
        $this->increment('total_withdrawn', $amount);

        return PokerTransaction::create([
            'user_id' => $this->user_id,
            'type' => 'withdraw',
            'amount' => -$amount,
            'balance_after' => $this->fresh()->chips_balance,
            'description' => $description,
        ]);
    }
}
