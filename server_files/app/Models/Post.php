<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Post extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'board_id', 'user_id', 'title', 'content', 'thumbnail',
        'images', 'is_pinned', 'is_notice', 'is_anonymous', 'status',
    ];

    protected $casts = [
        'images' => 'array',
        'is_pinned' => 'boolean',
        'is_notice' => 'boolean',
        'is_anonymous' => 'boolean',
    ];

    public function board() { return $this->belongsTo(Board::class); }
    public function user() { return $this->belongsTo(User::class); }
    public function comments() { return $this->hasMany(Comment::class); }
    public function likes() { return $this->hasMany(PostLike::class); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
    public function reports() { return $this->morphMany(Report::class, 'reportable'); }

    public function isLikedBy(?User $user): bool {
        if (!$user) return false;
        return $this->likes()->where('user_id', $user->id)->exists();
    }
}
