<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class RecipeComment extends Model {
    protected $table = 'recipe_comments';
    protected $fillable = ['recipe_id', 'user_id', 'content', 'rating'];
    public function recipe() { return $this->belongsTo(RecipePost::class, 'recipe_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
