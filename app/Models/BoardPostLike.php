<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BoardPostLike extends Model
{
    public $timestamps = false;

    protected $fillable = ['post_id', 'user_id'];

    public function post()
    {
        return $this->belongsTo(BoardPost::class, 'post_id');
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
