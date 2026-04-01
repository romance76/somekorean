<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class RealEstateListing extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'user_id', 'title', 'description', 'type', 'price', 'deposit',
        'address', 'region', 'latitude', 'longitude',
        'bedrooms', 'bathrooms', 'sqft', 'photos',
        'move_in_date', 'pet_policy', 'phone', 'email',
        'is_pinned', 'status',
    ];

    protected $casts = [
        'photos'    => 'array',
        'is_pinned' => 'boolean',
        'price'     => 'decimal:2',
        'deposit'   => 'decimal:2',
    ];

    public function user() { return $this->belongsTo(User::class); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
}

