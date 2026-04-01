<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ElderCheckinLog extends Model
{
    protected $fillable = [
        'user_id', 'checkin_date', 'checked_at', 'status',
        'alert_sent_at', 'guardian_notified',
    ];

    protected $casts = [
        'checkin_date'      => 'date',
        'checked_at'        => 'datetime',
        'alert_sent_at'     => 'datetime',
        'guardian_notified'  => 'boolean',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function elderSetting()
    {
        return $this->hasOne(ElderSetting::class, 'user_id', 'user_id');
    }
}
