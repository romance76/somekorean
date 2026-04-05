<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ClubPost extends Model
{
    use HasFactory;

    protected $fillable = [
        'club_id', 'user_id', 'title', 'content', 'images',
        'like_count', 'comment_count',
    ];

    protected function casts(): array
    {
        return [
            'images' => 'array',
            'like_count' => 'integer',
            'comment_count' => 'integer',
        ];
    }

    public function club()     { return $this->belongsTo(Club::class); }
    public function user()     { return $this->belongsTo(User::class); }
    public function comments() { return $this->morphMany(Comment::class, 'commentable'); }
}
