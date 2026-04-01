<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class BusinessEvent extends Model {
    protected $fillable = ['business_id','title','description','image_url','event_date','event_time','is_active'];
    protected $casts = ['event_date'=>'date','is_active'=>'boolean'];
    public function business() { return $this->belongsTo(Business::class); }
}
