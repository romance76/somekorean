<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\Response;

class DetectBot
{
    public function handle(Request $request, Closure $next): Response
    {
        // 글쓰기 요청만 체크 (POST 메서드 + 특정 URL 패턴)
        if ($request->isMethod('post') && $this->isWriteAction($request)) {
            $ip = $request->ip();
            $key = "write_rate:{$ip}";

            // 1분 내 5회 초과 체크
            $count = Cache::get($key, 0);
            if ($count >= 5) {
                try {
                    DB::table('ip_bans')->insertOrIgnore([
                        'ip_address' => $ip,
                        'reason'     => '자동 차단: 1분 내 글쓰기 5회 초과 (봇 의심)',
                        'expires_at' => now()->addHour(),
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                } catch (\Exception $e) {
                    // ip_bans 테이블 없으면 무시
                }
                return response()->json(['error' => '너무 많은 요청입니다. 잠시 후 다시 시도하세요.'], 429);
            }
            Cache::put($key, $count + 1, 60);

            // Honeypot 필드 체크
            if ($request->filled('website_url_confirm')) {
                try {
                    DB::table('ip_bans')->insertOrIgnore([
                        'ip_address' => $ip,
                        'reason'     => '자동 차단: Honeypot 필드 감지 (봇)',
                        'expires_at' => now()->addDay(),
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                } catch (\Exception $e) {
                    // ip_bans 테이블 없으면 무시
                }
                return response()->json(['error' => '요청을 처리할 수 없습니다.'], 403);
            }
        }

        return $next($request);
    }

    private function isWriteAction(Request $request): bool
    {
        $writePatterns = ['posts', 'comments', 'market', 'jobs', 'realestate', 'qa', 'recipes'];
        $path = $request->path();
        foreach ($writePatterns as $pattern) {
            if (str_contains($path, $pattern)) {
                return true;
            }
        }
        return false;
    }
}
