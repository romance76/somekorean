<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class News extends Model
{
    use HasFactory;

    protected $fillable = [
        'title', 'content', 'summary', 'source', 'source_url',
        'image_url', 'category_id', 'subcategory',
        'view_count', 'published_at',
    ];

    protected function casts(): array
    {
        return [
            'published_at' => 'datetime',
            'view_count' => 'integer',
        ];
    }

    public function category()  { return $this->belongsTo(NewsCategory::class, 'category_id'); }
    public function comments()  { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
