<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class RecipePost extends Model
{
    protected $fillable = [
        'source',
        'ext_id',
        'title',
        'category',
        'cook_method',
        'ingredients',
        'calories',
        'carbs',
        'protein',
        'fat',
        'sodium',
        'steps',
        'thumbnail',
        'hash_tags',
        'view_count',
        'like_count',
        'is_active',
    ];

    protected $casts = [
        'steps' => 'array',
        'is_active' => 'boolean',
    ];
}
