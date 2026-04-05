<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Short extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'title', 'video_url', 'thumbnail_url', 'youtube_id',
        'duration', 'view_count', 'like_count', 'comment_count', 'is_active',
    ];

    protected function casts(): array
    {
        return [
            'is_active' => 'boolean',
            'duration' => 'integer',
            'view_count' => 'integer',
            'like_count' => 'integer',
            'comment_count' => 'integer',
        ];
    }

    public function user()      { return $this->belongsTo(User::class); }
    public function likes()     { return $this->hasMany(ShortLike::class); }
    public function comments()  { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
