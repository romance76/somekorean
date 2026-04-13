<?php

namespace App\Events;

use App\Models\Call;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class CallInitiated implements ShouldBroadcastNow
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(public Call $call) {}

    public function broadcastOn(): array
    {
        return [new PrivateChannel('user.' . $this->call->callee_id)];
    }

    public function broadcastWith(): array
    {
        $caller = $this->call->caller;
        return [
            'call_id'       => $this->call->id,
            'room_id'       => $this->call->room_id,
            'caller_id'     => $this->call->caller_id,
            'caller_name'   => $this->call->call_type === 'elder' ? '안심서비스' : ($caller->name ?? '알 수 없음'),
            'caller_avatar' => $this->call->call_type === 'elder' ? '' : ($caller->avatar ?? ''),
            'call_type'     => $this->call->call_type ?? 'friend',
        ];
    }

    public function broadcastAs(): string
    {
        return 'call.initiated';
    }
}
