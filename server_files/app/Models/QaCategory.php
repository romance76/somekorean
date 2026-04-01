<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class QaCategory extends Model {
    protected $table = 'qa_categories';
    protected $fillable = ['name', 'key', 'icon', 'color', 'sort_order', 'is_active'];
    protected $casts = ['is_active' => 'boolean'];
    public function posts() { return $this->hasMany(QaPost::class, 'category_id'); }
}
