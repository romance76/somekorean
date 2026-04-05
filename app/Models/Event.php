<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Event extends Model
{
    use HasFactory;

    protected $fillable = [
        'title', 'description', 'content', 'image_url', 'category',
        'organizer', 'venue', 'address', 'city', 'state', 'zipcode',
        'lat', 'lng', 'start_date', 'end_date', 'price', 'url',
        'source', 'source_id', 'view_count', 'attendee_count',
    ];

    protected function casts(): array
    {
        return [
            'start_date' => 'datetime',
            'end_date' => 'datetime',
            'view_count' => 'integer',
            'attendee_count' => 'integer',
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

    public function attendees() { return $this->hasMany(EventAttendee::class); }
    public function comments()  { return $this->morphMany(Comment::class, 'commentable'); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}
