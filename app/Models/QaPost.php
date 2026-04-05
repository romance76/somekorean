<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class QaPost extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'category_id', 'title', 'content',
        'bounty_points', 'view_count', 'answer_count',
        'is_resolved', 'best_answer_id',
    ];

    protected function casts(): array
    {
        return [
            'bounty_points' => 'integer',
            'view_count' => 'integer',
            'answer_count' => 'integer',
            'is_resolved' => 'boolean',
        ];
    }

    public function user()       { return $this->belongsTo(User::class); }
    public function category()   { return $this->belongsTo(QaCategory::class, 'category_id'); }
    public function answers()    { return $this->hasMany(QaAnswer::class); }
    public function bestAnswer() { return $this->belongsTo(QaAnswer::class, 'best_answer_id'); }
    public function comments()   { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks()  { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
