<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class ClubPost extends Model
{
    protected $fillable = ['club_id','board_id','user_id','title','content','images','like_count','comment_count','is_pinned'];
    protected $casts = ['images'=>'array','is_pinned'=>'boolean'];
    public function club() { return $this->belongsTo(Club::class); }
    public function board() { return $this->belongsTo(ClubBoard::class, 'board_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
