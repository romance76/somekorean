<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ElderSetting extends Model
{
    protected $fillable = [
        'user_id', 'elder_mode', 'guardian_name', 'guardian_phone', 'guardian_user_id',
        'guardian2_name', 'guardian2_phone', 'checkin_interval', 'checkin_time',
        'checkin_enabled', 'sos_enabled', 'auto_call_enabled',
        'last_checkin_at', 'last_sos_at', 'alert_sent', 'missed_count',
        'timezone', 'notes', 'medication_times',
    ];

    protected $casts = [
        'elder_mode'        => 'boolean',
        'checkin_enabled'   => 'boolean',
        'sos_enabled'       => 'boolean',
        'auto_call_enabled' => 'boolean',
        'alert_sent'        => 'boolean',
        'last_checkin_at'   => 'datetime',
        'last_sos_at'       => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function guardian()
    {
        return $this->belongsTo(User::class, 'guardian_user_id');
    }

    public function checkinLogs()
    {
        return $this->hasMany(ElderCheckinLog::class, 'user_id', 'user_id');
    }
}
