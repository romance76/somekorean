<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class Friend extends Model
{
    protected $fillable = ['user_id','friend_id','status','source','expires_at'];
    protected $casts = ['expires_at' => 'datetime'];

    public function user() { return $this->belongsTo(User::class); }
    public function friend() { return $this->belongsTo(User::class, 'friend_id'); }

    public function isExpired(): bool
    {
        return $this->expires_at && $this->expires_at->isPast();
    }

    public function canCancel(): bool
    {
        return $this->status === 'pending'
            && $this->created_at->diffInHours(now()) >= 24;
    }
}
