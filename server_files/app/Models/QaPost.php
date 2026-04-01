<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class QaPost extends Model {
    protected $table = 'qa_posts';
    protected $fillable = ['category_id', 'user_id', 'title', 'content', 'region', 'status', 'source', 'view_count', 'answer_count', 'like_count', 'best_answer_id', 'is_pinned', 'is_hidden'];
    protected $casts = ['is_pinned' => 'boolean', 'is_hidden' => 'boolean'];
    public function category() { return $this->belongsTo(QaCategory::class, 'category_id'); }
    public function user() { return $this->belongsTo(User::class); }
    public function answers() { return $this->hasMany(QaAnswer::class, 'qa_post_id'); }
    public function bestAnswer() { return $this->belongsTo(QaAnswer::class, 'best_answer_id'); }
}
