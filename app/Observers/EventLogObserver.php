<?php

namespace App\Observers;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

/**
 * 범용 event_log Observer (Phase 2-C Post).
 * 모델 created 이벤트에 연결해 자동 기록.
 * Analytics 실시간 피드용.
 */
class EventLogObserver
{
    public function created(Model $model): void
    {
        try {
            $type = strtolower(class_basename($model));
            DB::table('event_log')->insert([
                'user_id'     => $model->user_id ?? auth()->id(),
                'event_type'  => $type . '.created',
                'target_type' => $type,
                'target_id'   => $model->id,
                'meta'        => json_encode([
                    'title' => $model->title ?? $model->name ?? $model->content ?? null,
                ], JSON_UNESCAPED_UNICODE),
                'ip'          => request()?->ip(),
                'user_agent'  => substr(request()?->userAgent() ?? '', 0, 500),
                'occurred_at' => now(),
            ]);
        } catch (\Throwable $e) {
            Log::warning('EventLog observer failed: ' . $e->getMessage());
        }
    }

    public function deleted(Model $model): void
    {
        try {
            $type = strtolower(class_basename($model));
            DB::table('event_log')->insert([
                'user_id'     => auth()->id(),
                'event_type'  => $type . '.deleted',
                'target_type' => $type,
                'target_id'   => $model->id,
                'meta'        => json_encode([
                    'deleted_by' => auth()->user()?->nickname ?? auth()->id(),
                ], JSON_UNESCAPED_UNICODE),
                'ip'          => request()?->ip(),
                'occurred_at' => now(),
            ]);
        } catch (\Throwable $e) {}
    }
}
