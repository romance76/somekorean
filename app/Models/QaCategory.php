<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class QaCategory extends Model
{
    use HasFactory;

    protected $fillable = [
        'name', 'slug', 'sort_order',
    ];

    protected function casts(): array
    {
        return [
            'sort_order' => 'integer',
        ];
    }

    public function posts() { return $this->hasMany(QaPost::class, 'category_id'); }
}
