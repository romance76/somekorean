<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class BoardPost extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'user_id', 'category_slug', 'title', 'content',
        'is_anonymous', 'view_count', 'like_count', 'comment_count',
    ];

    protected $casts = [
        'is_anonymous' => 'boolean',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function comments()
    {
        return $this->hasMany(BoardComment::class, 'post_id');
    }

    public function likes()
    {
        return $this->hasMany(BoardPostLike::class, 'post_id');
    }
}
