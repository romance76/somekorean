<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class JobPost extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'title', 'company', 'content', 'category', 'type',
        'salary_min', 'salary_max', 'salary_type',
        'lat', 'lng', 'city', 'state', 'zipcode',
        'contact_email', 'contact_phone',
        'is_active', 'expires_at', 'view_count',
    ];

    protected function casts(): array
    {
        return [
            'is_active' => 'boolean',
            'expires_at' => 'datetime',
            'salary_min' => 'integer',
            'salary_max' => 'integer',
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
