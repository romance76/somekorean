<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class RecipeRating extends Model
{
    protected $fillable = ['user_id', 'recipe_id', 'rating', 'comment'];

    protected $casts = ['rating' => 'integer'];

    public function recipe()
    {
        return $this->belongsTo(RecipePost::class, 'recipe_id');
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
