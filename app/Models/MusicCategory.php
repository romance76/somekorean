<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class MusicCategory extends Model {
    protected $fillable = ['name', 'slug', 'description', 'icon', 'sort_order', 'is_active', 'created_by'];
    protected $casts = ['is_active' => 'boolean'];

    public function tracks() {
        return $this->hasMany(MusicTrack::class, 'category_id')->orderBy('sort_order')->orderBy('id');
    }

    public function creator() {
        return $this->belongsTo(User::class, 'created_by');
    }

    protected static function boot() {
        parent::boot();
        static::creating(function ($cat) {
            if (!$cat->slug) $cat->slug = Str::slug($cat->name);
        });
    }
}
