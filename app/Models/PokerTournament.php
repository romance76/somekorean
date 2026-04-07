<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PokerTournament extends Model
{
    protected $fillable = [
        'title', 'type', 'status', 'buy_in', 'starting_chips',
        'max_players', 'min_players', 'scheduled_at', 'registration_opens_at',
        'started_at', 'finished_at', 'late_reg_levels', 'blind_level',
        'prize_pool', 'bounty_pct', 'schedule_pattern', 'is_template',
    ];

    protected function casts(): array
    {
        return [
            'scheduled_at' => 'datetime',
            'registration_opens_at' => 'datetime',
            'started_at' => 'datetime',
            'finished_at' => 'datetime',
            'prize_pool' => 'array',
            'buy_in' => 'integer',
            'starting_chips' => 'integer',
            'max_players' => 'integer',
            'min_players' => 'integer',
            'blind_level' => 'integer',
            'bounty_pct' => 'integer',
            'schedule_pattern' => 'array',
            'is_template' => 'boolean',
        ];
    }

    public function entries() { return $this->hasMany(PokerTournamentEntry::class, 'tournament_id'); }
    public function tables() { return $this->hasMany(PokerTournamentTable::class, 'tournament_id'); }

    public function registeredCount() { return $this->entries()->whereNotIn('status', ['eliminated', 'finished'])->count(); }
    public function onlineCount() { return $this->entries()->where('is_online', true)->count(); }

    public function scopeUpcoming($q) { return $q->whereIn('status', ['scheduled', 'registering'])->orderBy('scheduled_at'); }
    public function scopeRunning($q) { return $q->where('status', 'running'); }
}
