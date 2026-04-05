<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Club extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'name', 'description', 'category', 'image',
        'type', 'zipcode', 'member_count', 'is_active',
    ];

    protected function casts(): array
    {
        return [
            'is_active' => 'boolean',
            'member_count' => 'integer',
        ];
    }

    public function user()    { return $this->belongsTo(User::class); }
    public function members() { return $this->hasMany(ClubMember::class); }
    public function posts()   { return $this->hasMany(ClubPost::class); }
}
