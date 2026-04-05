<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class RealEstateListing extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'title', 'content', 'type', 'property_type',
        'price', 'deposit', 'images',
        'address', 'city', 'state', 'zipcode', 'lat', 'lng',
        'bedrooms', 'bathrooms', 'sqft',
        'is_active', 'view_count', 'contact_phone', 'contact_email',
    ];

    protected function casts(): array
    {
        return [
            'images' => 'array',
            'is_active' => 'boolean',
            'price' => 'integer',
            'deposit' => 'integer',
            'bedrooms' => 'integer',
            'bathrooms' => 'decimal:1',
            'sqft' => 'integer',
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

    public function user()      { return $this->belongsTo(User::class); }
    public function comments()  { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
