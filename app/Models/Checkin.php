<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Checkin extends Model
{
    public $timestamps = false;
    protected $fillable = ['user_id', 'checkin_date', 'streak_days'];
    protected $casts = ['checkin_date' => 'date', 'created_at' => 'datetime'];

    public function user() { return $this->belongsTo(User::class); }
}
