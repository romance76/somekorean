<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class RecipePost extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'title', 'title_ko', 'content', 'content_ko',
        'ingredients', 'ingredients_ko', 'steps', 'steps_ko',
        'category_id', 'images', 'servings', 'prep_time', 'cook_time',
        'difficulty', 'view_count', 'like_count', 'comment_count',
    ];

    protected function casts(): array
    {
        return [
            'ingredients' => 'array',
            'ingredients_ko' => 'array',
            'steps' => 'array',
            'steps_ko' => 'array',
            'images' => 'array',
            'servings' => 'integer',
            'prep_time' => 'integer',
            'cook_time' => 'integer',
            'view_count' => 'integer',
            'like_count' => 'integer',
            'comment_count' => 'integer',
        ];
    }

    public function user()      { return $this->belongsTo(User::class); }
    public function category()  { return $this->belongsTo(RecipeCategory::class, 'category_id'); }
    public function comments()  { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
