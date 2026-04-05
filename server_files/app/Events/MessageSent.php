<?php

namespace App\Events;

use App\Models\ChatMessage;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class MessageSent implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(public ChatMessage $message)
    {
    }

    public function broadcastOn(): array
    {
        return [
            new Channel('chat.' . $this->message->chat_room_id),
        ];
    }

    public function broadcastAs(): string
    {
        return 'message.sent';
    }

    public function broadcastWith(): array
    {
        return [
            'id'         => $this->message->id,
            'message'    => $this->message->message,
            'type'       => $this->message->type,
            'created_at' => $this->message->created_at->toISOString(),
            'user'       => [
                'id'            => $this->message->user->id,
                'name'          => $this->message->user->name,
                'nickname'      => $this->message->user->nickname,
                'profile_photo' => $this->message->user->profile_photo,
            ],
        ];
    }
}
