<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class QaAnswerLike extends Model
{
    public $timestamps = false;

    protected $fillable = ['answer_id', 'user_id'];

    public function answer()
    {
        return $this->belongsTo(QaAnswer::class, 'answer_id');
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
