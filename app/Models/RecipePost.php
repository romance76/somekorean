<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class RecipePost extends Model {
    protected $table = 'recipe_posts';
    protected $fillable = ['category_id', 'user_id', 'title', 'title_ko', 'intro', 'intro_ko', 'difficulty', 'cook_time', 'calories', 'servings', 'ingredients', 'ingredients_ko', 'steps', 'steps_ko', 'tips', 'tips_ko', 'tags', 'image_url', 'image_credit', 'view_count', 'like_count', 'bookmark_count', 'source', 'source_url', 'is_hidden'];
    protected $casts = ['ingredients' => 'array', 'ingredients_ko' => 'array', 'steps' => 'array', 'steps_ko' => 'array', 'tips' => 'array', 'tips_ko' => 'array', 'tags' => 'array', 'is_hidden' => 'boolean'];

    // 한글 우선 표시 접근자
    public function getDisplayTitleAttribute(): string {
        return $this->title_ko ?: $this->title;
    }
    public function getDisplayIntroAttribute(): ?string {
        return $this->intro_ko ?: $this->intro;
    }
    public function getDisplayIngredientsAttribute(): ?array {
        return $this->ingredients_ko ?: $this->ingredients;
    }
    public function getDisplayStepsAttribute(): ?array {
        return $this->steps_ko ?: $this->steps;
    }
    public function getDisplayTipsAttribute(): ?array {
        return $this->tips_ko ?: $this->tips;
    }
    public function category() { return $this->belongsTo(RecipeCategory::class, 'category_id'); }
    public function user() { return $this->belongsTo(User::class); }
    public function comments() { return $this->hasMany(RecipeComment::class, 'recipe_id'); }
}
