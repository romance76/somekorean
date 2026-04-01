<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MusicTrack extends Model {
    protected $fillable = ['category_id', 'title', 'artist', 'youtube_url', 'youtube_id', 'thumbnail', 'duration_seconds', 'sort_order', 'is_active', 'added_by', 'play_count'];
    protected $casts = ['is_active' => 'boolean'];

    public function category() {
        return $this->belongsTo(MusicCategory::class, 'category_id');
    }

    public function addedBy() {
        return $this->belongsTo(User::class, 'added_by');
    }

    public static function extractYoutubeId(string $url): ?string {
        preg_match('/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/', $url, $matches);
        return $matches[1] ?? null;
    }

    public static function getThumbnail(string $youtubeId): string {
        return "https://img.youtube.com/vi/{$youtubeId}/mqdefault.jpg";
    }
}
