<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class NewsCategory extends Model
{
    protected $fillable = ['name','slug','parent_id'];
    public function parent() { return $this->belongsTo(NewsCategory::class, 'parent_id'); }
    public function children() { return $this->hasMany(NewsCategory::class, 'parent_id'); }
    public function news() { return $this->hasMany(News::class, 'category_id'); }
}
