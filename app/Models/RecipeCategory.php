<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class RecipeCategory extends Model {
    protected $table = 'recipe_categories';
    protected $fillable = ['name', 'key', 'icon', 'sort_order', 'is_active'];
    protected $casts = ['is_active' => 'boolean'];
    public function posts() { return $this->hasMany(RecipePost::class, 'category_id'); }
}
