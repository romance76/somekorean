<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MentorRequest extends Model
{
    protected $fillable = ['mentor_id', 'mentee_id', 'message', 'status'];

    public function mentor() { return $this->belongsTo(Mentor::class); }
    public function mentee() { return $this->belongsTo(User::class, 'mentee_id'); }
}
