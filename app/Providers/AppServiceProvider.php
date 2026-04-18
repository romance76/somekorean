<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void {}

    public function boot(): void
    {
        // Phase 2-C Post: event_log 자동 기록 (주요 모델 created/deleted)
        if (\Schema::hasTable('event_log')) {
            $observable = [
                \App\Models\Post::class,
                \App\Models\Comment::class,
                \App\Models\MarketItem::class,
                \App\Models\RealEstateListing::class,
                \App\Models\Job::class,
            ];
            foreach ($observable as $cls) {
                if (class_exists($cls)) {
                    $cls::observe(\App\Observers\EventLogObserver::class);
                }
            }
        }
    }
}
