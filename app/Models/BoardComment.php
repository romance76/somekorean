<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class BoardComment extends Model
{
    use SoftDeletes;

    public $timestamps = false;

    protected $fillable = [
        'post_id', 'user_id', 'parent_id', 'content',
        'is_anonymous', 'like_count',
    ];

    protected $casts = [
        'is_anonymous' => 'boolean',
        'created_at' => 'datetime',
    ];

    public function post()
    {
        return $this->belongsTo(BoardPost::class, 'post_id');
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function parent()
    {
        return $this->belongsTo(BoardComment::class, 'parent_id');
    }

    public function replies()
    {
        return $this->hasMany(BoardComment::class, 'parent_id');
    }
}
