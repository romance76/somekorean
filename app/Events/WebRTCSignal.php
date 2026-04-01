<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class WebRTCSignal implements ShouldBroadcastNow
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(
        public readonly string $type,    // offer | answer | ice-candidate | call-request | call-end
        public readonly array  $payload, // SDP or ICE candidate
        public readonly int    $fromUserId,
        public readonly int    $toUserId,
        public readonly string $callId,
    ) {}

    public function broadcastOn(): Channel
    {
        return new PrivateChannel("call.{$this->toUserId}");
    }

    public function broadcastAs(): string
    {
        return 'webrtc.signal';
    }
}
