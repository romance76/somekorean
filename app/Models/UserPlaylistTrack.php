<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserPlaylistTrack extends Model
{
    use HasFactory;

    protected $fillable = [
        'playlist_id', 'track_id', 'sort_order',
    ];

    protected function casts(): array
    {
        return [
            'sort_order' => 'integer',
        ];
    }

    public function playlist() { return $this->belongsTo(UserPlaylist::class, 'playlist_id'); }
    public function track()    { return $this->belongsTo(MusicTrack::class, 'track_id'); }
}
