<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserPlaylist extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'name',
    ];

    public function user()   { return $this->belongsTo(User::class); }
    public function tracks() { return $this->belongsToMany(MusicTrack::class, 'user_playlist_tracks', 'playlist_id', 'track_id')->withPivot('sort_order')->orderByPivot('sort_order'); }
}
