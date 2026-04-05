<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class RecipePost extends Model {
    protected $table = 'recipe_posts';
    protected $fillable = ['category_id', 'user_id', 'title', 'title_ko', 'intro', 'intro_ko', 'difficulty', 'cook_time', 'calories', 'servings', 'ingredients', 'ingredients_ko', 'steps', 'steps_ko', 'tips', 'tips_ko', 'tags', 'image_url', 'image_credit', 'view_count', 'like_count', 'bookmark_count', 'source', 'source_url', 'is_hidden'];
    protected $casts = ['ingredients' => 'array', 'ingredients_ko' => 'array', 'steps' => 'array', 'steps_ko' => 'array', 'tips' => 'array', 'tips_ko' => 'array', 'tags' => 'array', 'is_hidden' => 'boolean'];
    public function category() { return $this->belongsTo(RecipeCategory::class, 'category_id'); }
    public function user() { return $this->belongsTo(User::class); }
    public function comments() { return $this->hasMany(RecipeComment::class, 'recipe_id'); }
}
