<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ChatRoom extends Model
{
    use HasFactory;

    protected $fillable = [
        'name', 'type', 'created_by',
    ];

    public function creator()  { return $this->belongsTo(User::class, 'created_by'); }
    public function users()    { return $this->belongsToMany(User::class, 'chat_room_users')->withPivot('last_read_at')->withTimestamps(); }
    public function messages() { return $this->hasMany(ChatMessage::class); }
}
