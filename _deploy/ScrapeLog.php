<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class ScrapeLog extends Model
{
    protected $fillable = ['store_id','status','deals_count','error_message','started_at','finished_at'];
    protected $casts = ['started_at'=>'datetime','finished_at'=>'datetime'];
    public function store() { return $this->belongsTo(ShoppingStore::class, 'store_id'); }
}
