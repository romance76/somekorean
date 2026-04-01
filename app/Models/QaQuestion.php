<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class QaQuestion extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'user_id', 'category_slug', 'title', 'content',
        'point_reward', 'accepted_answer_id', 'is_resolved',
        'view_count', 'answer_count', 'recommend_count', 'resolved_at',
    ];

    protected $casts = [
        'is_resolved' => 'boolean',
        'point_reward' => 'integer',
        'resolved_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function answers()
    {
        return $this->hasMany(QaQuestionAnswer::class, 'question_id');
    }

    public function recommends()
    {
        return $this->hasMany(QaQuestionRecommend::class, 'question_id');
    }

    public function acceptedAnswer()
    {
        return $this->belongsTo(QaQuestionAnswer::class, 'accepted_answer_id');
    }
}
