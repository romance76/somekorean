<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class StoreFlyer extends Model
{
    protected $fillable = ['store_id','title','image_url','valid_from','valid_until','is_active'];
    protected $casts = ['is_active'=>'boolean','valid_from'=>'date','valid_until'=>'date'];
    public function store() { return $this->belongsTo(ShoppingStore::class, 'store_id'); }
}
