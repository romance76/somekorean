<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class QaAnswer extends Model
{
    use HasFactory;

    protected $fillable = [
        'qa_post_id', 'user_id', 'content', 'like_count', 'is_best',
    ];

    protected function casts(): array
    {
        return [
            'like_count' => 'integer',
            'is_best' => 'boolean',
        ];
    }

    public function qaPost() { return $this->belongsTo(QaPost::class); }
    public function user()   { return $this->belongsTo(User::class); }
}
