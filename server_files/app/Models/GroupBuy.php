<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GroupBuy extends Model
{
    protected $fillable = [
        'user_id', 'title', 'description', 'product_url', 'images',
        'target_price', 'min_participants', 'max_participants',
        'category', 'deadline', 'status',
    ];

    protected $casts = [
        'images'   => 'array',
        'deadline' => 'datetime',
        'target_price' => 'decimal:2',
    ];

    protected $appends = ['participants_count', 'is_joined'];

    public function user()        { return $this->belongsTo(User::class); }
    public function participants(){ return $this->hasMany(GroupBuyParticipant::class); }

    public function getParticipantsCountAttribute()
    {
        return $this->participants()->count();
    }

    public function getIsJoinedAttribute()
    {
        if (!auth()->check()) return false;
        return $this->participants()->where('user_id', auth()->id())->exists();
    }
}
