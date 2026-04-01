<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ClubPost extends Model
{
    protected $fillable = [
        'club_id', 'user_id', 'title', 'content', 'view_count', 'like_count',
    ];

    public function club() { return $this->belongsTo(Club::class); }
    public function user() { return $this->belongsTo(User::class); }
}
