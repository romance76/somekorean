<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class QaAnswer extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'question_id', 'user_id', 'content',
        'is_accepted', 'like_count',
    ];

    protected $casts = [
        'is_accepted' => 'boolean',
    ];

    public function question()
    {
        return $this->belongsTo(QaQuestion::class, 'question_id');
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function likes()
    {
        return $this->hasMany(QaAnswerLike::class, 'answer_id');
    }
}
