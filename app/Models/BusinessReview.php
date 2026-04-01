<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BusinessReview extends Model
{
    protected $fillable = [
        'business_id', 'user_id', 'rating', 'content', 'photos',
        'visit_date', 'sub_ratings', 'is_visible', 'report_count',
        'owner_reply', 'owner_replied_at',
    ];

    protected $casts = [
        'photos' => 'array',
        'sub_ratings' => 'array',
        'is_visible' => 'boolean',
        'visit_date' => 'date',
        'owner_replied_at' => 'datetime',
    ];

    public function business() { return $this->belongsTo(Business::class); }
    public function user() { return $this->belongsTo(User::class); }
}
