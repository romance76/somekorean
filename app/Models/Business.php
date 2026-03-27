<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Business extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'owner_id', 'name', 'category', 'description', 'address',
        'lat', 'lng', 'phone', 'website', 'hours', 'photos',
        'region', 'is_verified', 'is_sponsored', 'status',
    ];

    protected $casts = [
        'hours' => 'array',
        'photos' => 'array',
        'is_verified' => 'boolean',
        'is_sponsored' => 'boolean',
    ];

    public function owner() { return $this->belongsTo(User::class, 'owner_id'); }
    public function reviews() { return $this->hasMany(BusinessReview::class); }
}
