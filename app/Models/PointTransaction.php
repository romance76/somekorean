<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PointTransaction extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'user_id', 'from_user_id', 'type', 'amount',
        'balance_after', 'reference_id', 'reference_type', 'description',
    ];

    protected $casts = [
        'amount' => 'integer',
        'balance_after' => 'integer',
        'created_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function fromUser()
    {
        return $this->belongsTo(User::class, 'from_user_id');
    }
}
