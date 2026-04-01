<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Business extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'owner_id', 'owner_user_id', 'name', 'name_ko', 'name_en',
        'category', 'description', 'address',
        'lat', 'lng', 'latitude', 'longitude',
        'phone', 'website', 'hours', 'photos',
        'region', 'is_verified', 'is_sponsored', 'status',
        'is_claimed', 'is_premium', 'premium_type', 'premium_expires_at',
        'google_place_id',
        'owner_description_ko', 'owner_description_en',
        'owner_photos', 'menu_items',
        'data_source', 'source_url',
        'temp_closed', 'temp_closed_note',
        'rating_avg', 'review_count',
    ];

    protected $casts = [
        'hours' => 'array',
        'photos' => 'array',
        'owner_photos' => 'array',
        'menu_items' => 'array',
        'is_verified' => 'boolean',
        'is_sponsored' => 'boolean',
        'is_claimed' => 'boolean',
        'is_premium' => 'boolean',
        'temp_closed' => 'boolean',
        'premium_expires_at' => 'datetime',
    ];

    public function owner() { return $this->belongsTo(User::class, 'owner_id'); }
    public function ownerUser() { return $this->belongsTo(User::class, 'owner_user_id'); }
    public function reviews() { return $this->hasMany(BusinessReview::class); }
    public function claims() { return $this->hasMany(BusinessClaim::class); }
    public function stats() { return $this->hasMany(BusinessStat::class); }
    public function events() { return $this->hasMany(BusinessEvent::class); }
}
