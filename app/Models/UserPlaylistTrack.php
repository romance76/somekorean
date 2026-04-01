<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class UserPlaylistTrack extends Model {
    protected $fillable = ['playlist_id', 'user_id', 'title', 'artist', 'youtube_url', 'youtube_id', 'thumbnail', 'duration_seconds', 'sort_order'];

    public function playlist() {
        return $this->belongsTo(UserPlaylist::class);
    }
}
