<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class ShoppingStore extends Model
{
    use SoftDeletes;
    protected $fillable = ['name','name_en','chain_name','category','logo_url','type','region','website','weekly_ad_url','rss_url','scrape_method','scrape_schedule','logo','description','is_active','memo','last_scraped_at'];
    protected $casts = ['is_active'=>'boolean','last_scraped_at'=>'datetime'];

    public function deals() { return $this->hasMany(ShoppingDeal::class, 'store_id'); }
    public function locations() { return $this->hasMany(StoreLocation::class, 'store_id'); }
    public function flyers() { return $this->hasMany(StoreFlyer::class, 'store_id'); }
    public function scrapeLogs() { return $this->hasMany(ScrapeLog::class, 'store_id'); }

    public function activeDeals() {
        return $this->deals()->where('is_active', true)
            ->where(function($q) {
                $q->whereNull('valid_until')->orWhere('valid_until', '>=', now());
            });
    }
}
