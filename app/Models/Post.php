<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    use HasFactory;

    protected $fillable = [
        'board_id', 'user_id', 'title', 'content', 'category', 'images',
        'view_count', 'like_count', 'comment_count',
        'is_pinned', 'is_hidden',
        'lat', 'lng', 'city', 'state', 'zipcode',
    ];

    protected function casts(): array
    {
        return [
            'images' => 'array',
            'is_pinned' => 'boolean',
            'is_hidden' => 'boolean',
            'view_count' => 'integer',
            'like_count' => 'integer',
            'comment_count' => 'integer',
            'lat' => 'decimal:7',
            'lng' => 'decimal:7',
        ];
    }

    public function scopeNearby($query, float $lat, float $lng, float $radiusMiles = 25)
    {
        $haversine = "(3959 * acos(cos(radians(?)) * cos(radians(lat)) * cos(radians(lng) - radians(?)) + sin(radians(?)) * sin(radians(lat))))";
        return $query->selectRaw("*, {$haversine} AS distance", [$lat, $lng, $lat])
                     ->havingRaw("distance <= ?", [$radiusMiles])
                     ->orderBy('distance');
    }

    public function board()    { return $this->belongsTo(Board::class); }
    public function user()     { return $this->belongsTo(User::class); }
    public function comments() { return $this->morphMany(Comment::class, 'commentable'); }
    public function likes()    { return $this->hasMany(PostLike::class); }
    public function bookmarks(){ return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
