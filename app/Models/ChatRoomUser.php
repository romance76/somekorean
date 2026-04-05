<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ChatRoomUser extends Model
{
    use HasFactory;

    protected $fillable = [
        'chat_room_id', 'user_id', 'last_read_at',
    ];

    protected function casts(): array
    {
        return [
            'last_read_at' => 'datetime',
        ];
    }

    public function chatRoom() { return $this->belongsTo(ChatRoom::class); }
    public function user()     { return $this->belongsTo(User::class); }
}
