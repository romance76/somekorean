<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class Club extends Model
{
    protected $fillable = ['user_id','name','description','category','image','type','zipcode','lat','lng','member_count','is_active'];
    protected $casts = ['is_active'=>'boolean','lat'=>'decimal:7','lng'=>'decimal:7'];
    public function scopeNearby($q,$lat,$lng,$r=50) { return $q->selectRaw("*, (3959*acos(cos(radians(?))*cos(radians(lat))*cos(radians(lng)-radians(?))+sin(radians(?))*sin(radians(lat)))) AS distance",[$lat,$lng,$lat])->having('distance','<',$r); }
    public function user() { return $this->belongsTo(User::class); }
    public function members() { return $this->hasMany(ClubMember::class); }
    public function posts() { return $this->hasMany(ClubPost::class); }
}
