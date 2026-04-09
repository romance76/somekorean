<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;
use Illuminate\Auth\AuthenticationException;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        channels: __DIR__.'/../routes/channels.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // 미들웨어 별칭 등록
        $middleware->alias([
            'admin'        => \App\Http\Middleware\AdminMiddleware::class,
            'check.ip.ban' => \App\Http\Middleware\CheckIpBan::class,
            'detect.bot'   => \App\Http\Middleware\DetectBot::class,
            'auth'         => \App\Http\Middleware\Authenticate::class,
        ]);

        // IP 차단 + 봇 감지 + 온라인 상태 미들웨어를 API 전체에 적용
        $middleware->api(prepend: [
            \App\Http\Middleware\CheckIpBan::class,
            \App\Http\Middleware\DetectBot::class,
        ]);
        $middleware->api(append: [
            \App\Http\Middleware\UpdateLastActive::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->render(function (AuthenticationException $e, Request $request) {
            if ($request->is('api/*') || $request->expectsJson()) {
                return response()->json([
                    'success' => false,
                    'message' => '인증이 필요합니다.',
                ], 401);
            }
        });
    })->create();
