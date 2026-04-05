<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class News extends Model
{
    protected $fillable = [
        'title',
        'summary',
        'content',
        'url',
        'source',
        'category',
        'image_url',
        'published_at',
        'category_id',
        'main_category_id',
        'is_featured',
        'is_digest',
        'view_count',
        'like_count',
    ];

    protected $casts = [
        'published_at' => 'datetime',
        'is_featured'  => 'boolean',
        'is_digest'    => 'boolean',
        'view_count'   => 'integer',
        'like_count'   => 'integer',
    ];

    /** 서브 카테고리 */
    public function subCategory(): BelongsTo
    {
        return $this->belongsTo(NewsCategory::class, 'category_id');
    }

    /** 메인 카테고리 */
    public function mainCategory(): BelongsTo
    {
        return $this->belongsTo(NewsCategory::class, 'main_category_id');
    }
}
