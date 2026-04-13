<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BannerAd extends Model
{
    protected $fillable = [
        'user_id', 'title', 'image_url', 'link_url',
        'page', 'position', 'geo_scope', 'geo_value',
        'start_date', 'end_date', 'daily_cost', 'total_cost',
        'impressions', 'clicks', 'status', 'reject_reason',
    ];

    protected $casts = [
        'start_date' => 'date',
        'end_date' => 'date',
    ];

    public function user() { return $this->belongsTo(User::class); }

    public function scopeActive($q) {
        return $q->where('status', 'active')
            ->where('start_date', '<=', now())
            ->where('end_date', '>=', now());
    }
}
