<?php

namespace App\Console\Commands;

use App\Models\PokerTournament;
use App\Events\PokerLobbyUpdate;
use Carbon\Carbon;
use Illuminate\Console\Command;

class GeneratePokerTournaments extends Command
{
    protected $signature = 'poker:generate-tournaments';
    protected $description = '스케줄 템플릿 기반으로 내일 토너먼트 자동 생성';

    public function handle()
    {
        $templates = PokerTournament::where('is_template', true)->get();
        $tomorrow = Carbon::tomorrow('America/New_York');
        $created = 0;

        foreach ($templates as $template) {
            $pattern = $template->schedule_pattern;
            if (!$pattern || empty($pattern['recurring'])) continue;

            $days = $pattern['days'] ?? ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
            $time = $pattern['time'] ?? '18:00';
            $dayMap = ['mon' => 1, 'tue' => 2, 'wed' => 3, 'thu' => 4, 'fri' => 5, 'sat' => 6, 'sun' => 0];

            // 내일이 스케줄 요일에 해당하는지
            $tomorrowDay = strtolower($tomorrow->format('D')); // mon, tue, ...
            $tomorrowDayShort = substr($tomorrowDay, 0, 3);

            if (!in_array($tomorrowDayShort, $days)) {
                $this->line("  ↳ {$template->title}: 내일({$tomorrowDayShort})은 스케줄 요일 아님, 건너뜀");
                continue;
            }

            // 이미 내일 같은 시간에 같은 제목으로 생성되어 있는지
            $scheduledAt = Carbon::parse($tomorrow->format('Y-m-d') . ' ' . $time, 'America/New_York')->utc();
            $exists = PokerTournament::where('title', $template->title)
                ->where('scheduled_at', $scheduledAt->format('Y-m-d H:i:s'))
                ->where('is_template', false)
                ->exists();

            if ($exists) {
                $this->line("  ↳ {$template->title}: 이미 생성됨, 건너뜀");
                continue;
            }

            PokerTournament::create([
                'title' => $template->title,
                'type' => $template->type,
                'status' => 'scheduled',
                'buy_in' => $template->buy_in,
                'starting_chips' => $template->starting_chips,
                'max_players' => $template->max_players,
                'min_players' => $template->min_players,
                'scheduled_at' => $scheduledAt,
                'registration_opens_at' => now(),
                'late_reg_levels' => $template->late_reg_levels,
                'bounty_pct' => $template->bounty_pct,
                'is_template' => false,
            ]);

            $created++;
            $this->info("✅ 생성: {$template->title} → {$scheduledAt}");
        }

        if ($created > 0) {
            broadcast(new PokerLobbyUpdate());
        }

        $this->info("총 {$created}개 토너먼트 생성 완료");
    }
}
