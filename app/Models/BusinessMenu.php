<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BusinessMenu extends Model
{
    protected $fillable = ['business_id', 'name', 'description', 'price', 'image', 'category', 'sort_order', 'is_available'];

    protected $casts = [
        'price' => 'decimal:2',
        'is_available' => 'boolean',
    ];

    public function business()
    {
        return $this->belongsTo(Business::class);
    }

    public function options()
    {
        return $this->hasMany(BusinessMenuOption::class);
    }
}
