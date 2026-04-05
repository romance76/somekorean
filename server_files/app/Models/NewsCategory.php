<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class NewsCategory extends Model
{
    protected $fillable = [
        'name',
        'name_en',
        'slug',
        'parent_id',
        'priority',
        'is_active',
        'icon',
        'color',
    ];

    protected $casts = [
        'is_active' => 'boolean',
    ];

    /** 부모 카테고리 (메인 카테고리) */
    public function parent(): BelongsTo
    {
        return $this->belongsTo(NewsCategory::class, 'parent_id');
    }

    /** 자식 카테고리 (서브 카테고리) */
    public function children(): HasMany
    {
        return $this->hasMany(NewsCategory::class, 'parent_id')->orderBy('priority');
    }

    /** 이 카테고리의 뉴스들 */
    public function news(): HasMany
    {
        return $this->hasMany(News::class, 'category_id');
    }

    /** 활성화된 카테고리만 */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }

    /** 메인 카테고리 (parent_id = null) */
    public function scopeMainCategories($query)
    {
        return $query->whereNull('parent_id')->orderBy('priority');
    }

    /** 서브 카테고리 (parent_id != null) */
    public function scopeSubCategories($query)
    {
        return $query->whereNotNull('parent_id')->orderBy('priority');
    }
}
