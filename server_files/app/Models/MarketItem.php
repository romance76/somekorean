<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class MarketItem extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'user_id', 'title', 'description', 'price', 'price_negotiable',
        'images', 'category', 'item_type', 'region', 'condition', 'status',
        'reservation_points', 'reservation_hours',
    ];

    protected $casts = [
        'images' => 'array',
        'price_negotiable' => 'boolean',
        'price' => 'decimal:2',
    ];

    public function user() { return $this->belongsTo(User::class); }
    public function bookmarks() { return $this->morphMany(Bookmark::class, 'bookmarkable'); }
    public function reservations() { return $this->hasMany(MarketReservation::class); }
}
