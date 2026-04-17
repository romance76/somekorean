<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class QaAnswer extends Model
{
    protected $fillable = ['qa_post_id','user_id','content','like_count','dislike_count','is_best'];
    protected $casts = ['is_best'=>'boolean'];
    public function post() { return $this->belongsTo(QaPost::class, 'qa_post_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
