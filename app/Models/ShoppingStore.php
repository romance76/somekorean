<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ShoppingStore extends Model
{
    use HasFactory;

    protected $fillable = [
        'name', 'logo', 'website', 'category',
    ];

    public function deals() { return $this->hasMany(ShoppingDeal::class, 'store_id'); }
}
