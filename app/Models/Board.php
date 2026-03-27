<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Board extends Model
{
    protected $fillable = ['name', 'slug', 'category', 'description', 'icon', 'sort_order', 'is_active'];

    public function posts() { return $this->hasMany(Post::class); }
}
