<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ClubBoard extends Model
{
    protected $fillable = ['club_id', 'name', 'description', 'sort_order', 'only_admin_post', 'is_active'];
    protected $casts = ['only_admin_post' => 'boolean', 'is_active' => 'boolean'];

    public function club() { return $this->belongsTo(Club::class); }
    public function posts() { return $this->hasMany(ClubPost::class, 'board_id'); }
}
