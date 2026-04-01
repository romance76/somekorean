<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class QaQuestionRecommend extends Model
{
    public $timestamps = false;

    protected $fillable = ['question_id', 'user_id'];

    public function question()
    {
        return $this->belongsTo(QaQuestion::class, 'question_id');
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
