<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ElderSetting extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'guardian_id', 'checkin_interval',
        'sos_contacts', 'medications', 'health_notes',
    ];

    protected function casts(): array
    {
        return [
            'sos_contacts' => 'array',
            'medications' => 'array',
            'checkin_interval' => 'integer',
        ];
    }

    public function user()     { return $this->belongsTo(User::class); }
    public function guardian() { return $this->belongsTo(User::class, 'guardian_id'); }
}
