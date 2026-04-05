<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ShortLike extends Model
{
    use HasFactory;

    protected $fillable = ['short_id', 'user_id'];

    public function short() { return $this->belongsTo(Short::class); }
    public function user()  { return $this->belongsTo(User::class); }
}
