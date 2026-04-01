<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class BusinessClaim extends Model {
    protected $fillable = [
        'business_id','user_id','status','email_token','email_verified_at',
        'document_urls','admin_note','reviewed_by','reviewed_at'
    ];
    protected $casts = ['document_urls'=>'array','email_verified_at'=>'datetime','reviewed_at'=>'datetime'];
    public function business() { return $this->belongsTo(Business::class); }
    public function user() { return $this->belongsTo(User::class); }
}
