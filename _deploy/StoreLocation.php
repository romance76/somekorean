<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class StoreLocation extends Model
{
    protected $fillable = ['store_id','branch_name','address','city','state','zip_code','lat','lng','phone','open_time','close_time','open_days','is_24h','is_active'];
    protected $casts = ['is_active'=>'boolean','is_24h'=>'boolean','open_days'=>'array','lat'=>'float','lng'=>'float'];

    public function store() { return $this->belongsTo(ShoppingStore::class, 'store_id'); }

    public function getIsOpenNowAttribute(): bool {
        if ($this->is_24h) return true;
        $now = now()->setTimezone('America/New_York');
        $openTime = \Carbon\Carbon::createFromFormat('H:i', $this->open_time ?? '09:00', 'America/New_York');
        $closeTime = \Carbon\Carbon::createFromFormat('H:i', $this->close_time ?? '21:00', 'America/New_York');
        return $now->between($openTime, $closeTime);
    }

    // Haversine scope
    public function scopeNearby($query, $lat, $lng, $radiusMiles = 30) {
        return $query->selectRaw("*, (3959 * acos(cos(radians(?)) * cos(radians(lat)) * cos(radians(lng) - radians(?)) + sin(radians(?)) * sin(radians(lat)))) AS distance", [$lat, $lng, $lat])
            ->having('distance', '<=', $radiusMiles)
            ->orderBy('distance');
    }
}
