<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PointLog extends Model
{
    public $timestamps = false;
    protected $fillable = ['user_id', 'type', 'action', 'amount', 'balance_after', 'ref_id', 'memo'];
    protected $casts = ['created_at' => 'datetime'];

    public function user() { return $this->belongsTo(User::class); }
}
