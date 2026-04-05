<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class QaAnswer extends Model {
    protected $table = 'qa_answers';
    protected $fillable = ['qa_post_id', 'user_id', 'content', 'is_best', 'like_count', 'source', 'is_hidden'];
    protected $casts = ['is_best' => 'boolean', 'is_hidden' => 'boolean'];
    public function post() { return $this->belongsTo(QaPost::class, 'qa_post_id'); }
    public function user() { return $this->belongsTo(User::class); }
}
