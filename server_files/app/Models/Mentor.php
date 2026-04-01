<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Mentor extends Model
{
    protected $fillable = [
        'user_id', 'field', 'bio', 'years_experience',
        'company', 'position', 'skills', 'is_available',
    ];

    protected $casts = [
        'skills'       => 'array',
        'is_available' => 'boolean',
    ];

    public function user()     { return $this->belongsTo(User::class); }
    public function requests() { return $this->hasMany(MentorRequest::class); }
}
