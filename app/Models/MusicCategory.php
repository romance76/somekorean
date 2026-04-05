<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MusicCategory extends Model
{
    use HasFactory;

    protected $fillable = [
        'name', 'slug', 'image', 'sort_order',
    ];

    protected function casts(): array
    {
        return [
            'sort_order' => 'integer',
        ];
    }

    public function tracks() { return $this->hasMany(MusicTrack::class, 'category_id'); }
}
