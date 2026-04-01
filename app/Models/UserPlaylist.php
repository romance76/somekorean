<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class UserPlaylist extends Model {
    protected $fillable = ['user_id', 'name', 'description', 'cover_image', 'is_public', 'play_count'];
    protected $casts = ['is_public' => 'boolean'];

    public function user() {
        return $this->belongsTo(User::class);
    }

    public function tracks() {
        return $this->hasMany(UserPlaylistTrack::class, 'playlist_id')->orderBy('sort_order')->orderBy('id');
    }
}
