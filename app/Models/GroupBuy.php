<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class GroupBuy extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'title', 'content', 'images', 'product_url',
        'original_price', 'group_price',
        'min_participants', 'max_participants', 'current_participants',
        'lat', 'lng', 'city', 'state',
        'status', 'deadline',
    ];

    protected function casts(): array
    {
        return [
            'images' => 'array',
            'original_price' => 'integer',
            'group_price' => 'integer',
            'min_participants' => 'integer',
            'max_participants' => 'integer',
            'current_participants' => 'integer',
            'deadline' => 'datetime',
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

    public function user()      { return $this->belongsTo(User::class); }
    public function comments()  { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
