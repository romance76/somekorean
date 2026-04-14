<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class GroupBuy extends Model
{
    protected $fillable = ['user_id','title','content','images','product_url','business_doc','original_price','group_price','discount_tiers','min_participants','max_participants','current_participants','lat','lng','city','state','status','end_type','payment_method','is_approved','approved_by','approved_at','rejection_reason','category','deadline'];
    protected $casts = ['images'=>'array','discount_tiers'=>'array','deadline'=>'datetime','approved_at'=>'datetime','lat'=>'decimal:7','lng'=>'decimal:7','original_price'=>'decimal:2','group_price'=>'decimal:2','is_approved'=>'boolean'];
    public function user() { return $this->belongsTo(User::class); }
    public function participants() { return $this->hasMany(GroupBuyParticipant::class); }
    public function approver() { return $this->belongsTo(User::class, 'approved_by'); }
    public function scopeNearby($q,$lat,$lng,$r=50) { return $q->selectRaw("*, (3959*acos(cos(radians(?))*cos(radians(lat))*cos(radians(lng)-radians(?))+sin(radians(?))*sin(radians(lat)))) AS distance",[$lat,$lng,$lat])->having('distance','<',$r); }
    public function scopeApproved($q) { return $q->where('is_approved', true); }
    // 현재 할인율 계산
    public function getCurrentDiscountAttribute() {
        if (!$this->discount_tiers) return 0;
        $tiers = collect($this->discount_tiers)->sortByDesc('min_people');
        foreach ($tiers as $tier) {
            if ($this->current_participants >= $tier['min_people']) return $tier['discount_pct'];
        }
        return 0;
    }
    public function getCurrentPriceAttribute() {
        $discount = $this->current_discount;
        return $discount > 0 ? round($this->original_price * (100 - $discount) / 100, 2) : $this->group_price ?: $this->original_price;
    }
}
