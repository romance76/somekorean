<?php

namespace App\Events;

use App\Models\PokerTournament;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class PokerTournamentUpdate implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public $tournament;

    public function __construct(PokerTournament $tournament)
    {
        $this->tournament = $tournament;
    }

    public function broadcastOn(): array
    {
        return [
            new Channel('poker.tournament.' . $this->tournament->id),
            new Channel('poker.lobby'),
        ];
    }

    public function broadcastAs(): string
    {
        return 'tournament.updated';
    }

    public function broadcastWith(): array
    {
        return [
            'id' => $this->tournament->id,
            'status' => $this->tournament->status,
            'registered_count' => $this->tournament->registered_count ?? $this->tournament->entries()->count(),
            'online_count' => $this->tournament->online_count ?? $this->tournament->entries()->where('is_online', true)->count(),
        ];
    }
}
