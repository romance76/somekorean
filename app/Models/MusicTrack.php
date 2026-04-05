<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MusicTrack extends Model
{
    use HasFactory;

    protected $fillable = [
        'category_id', 'title', 'artist', 'youtube_url', 'youtube_id',
        'duration', 'sort_order',
    ];

    protected function casts(): array
    {
        return [
            'duration' => 'integer',
            'sort_order' => 'integer',
        ];
    }

    public function category()  { return $this->belongsTo(MusicCategory::class, 'category_id'); }
    public function playlists() { return $this->belongsToMany(UserPlaylist::class, 'user_playlist_tracks', 'track_id', 'playlist_id')->withPivot('sort_order'); }
}
