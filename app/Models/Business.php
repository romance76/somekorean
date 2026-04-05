<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Business extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'name', 'description', 'category', 'subcategory',
        'phone', 'email', 'website', 'address', 'city', 'state', 'zipcode',
        'lat', 'lng', 'images', 'logo', 'hours',
        'rating', 'review_count', 'is_verified', 'is_claimed',
        'owner_id', 'view_count',
    ];

    protected function casts(): array
    {
        return [
            'images' => 'array',
            'hours' => 'array',
            'is_verified' => 'boolean',
            'is_claimed' => 'boolean',
            'rating' => 'decimal:2',
            'review_count' => 'integer',
            'view_count' => 'integer',
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

    public function user()    { return $this->belongsTo(User::class); }
    public function owner()   { return $this->belongsTo(User::class, 'owner_id'); }
    public function reviews() { return $this->hasMany(BusinessReview::class); }
    public function claims()  { return $this->hasMany(BusinessClaim::class); }
    public function comments(){ return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks(){ return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
