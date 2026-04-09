<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BusinessMenuOption extends Model
{
    protected $fillable = ['business_menu_id', 'name', 'price_add', 'sort_order'];

    protected $casts = [
        'price_add' => 'decimal:2',
    ];

    public function menu()
    {
        return $this->belongsTo(BusinessMenu::class, 'business_menu_id');
    }
}
