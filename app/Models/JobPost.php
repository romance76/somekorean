<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class JobPost extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'user_id', 'title', 'content', 'company_name', 'contact_email',
        'contact_phone', 'region', 'address', 'job_type', 'salary_range',
        'deadline', 'is_pinned', 'status',
    ];

    protected $casts = ['deadline' => 'date', 'is_pinned' => 'boolean'];

    public function user() { return $this->belongsTo(User::class); }
}
