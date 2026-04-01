<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class BusinessStat extends Model {
    protected $fillable = ['business_id','stat_date','views','clicks','phone_clicks','direction_clicks','website_clicks'];
    public function business() { return $this->belongsTo(Business::class); }
}
