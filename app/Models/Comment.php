<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Comment extends Model
{
    use HasFactory;

    protected $fillable = [
        'commentable_type', 'commentable_id', 'user_id',
        'parent_id', 'content', 'like_count', 'is_hidden',
    ];

    protected function casts(): array
    {
        return [
            'is_hidden' => 'boolean',
            'like_count' => 'integer',
        ];
    }

    public function commentable() { return $this->morphTo(); }
    public function user()        { return $this->belongsTo(User::class); }
    public function parent()      { return $this->belongsTo(Comment::class, 'parent_id'); }
    public function replies()     { return $this->hasMany(Comment::class, 'parent_id'); }
}
