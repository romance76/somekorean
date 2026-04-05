<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\Response;

class DetectBot
{
    /**
     * 봇 감지 및 레이트 리미팅 미들웨어
     * - API 요청: IP당 분당 최대 60회
     * - Honeypot: 'website_url' 히든 필드가 채워지면 차단
     * - 초과 시 429 응답
     */
    public function handle(Request $request, Closure $next): Response
    {
        $ip = $request->ip();

        // 1) Honeypot 필드 체크 (모든 POST 요청)
        if ($request->isMethod('post') && $request->filled('website_url')) {
            $this->autoBanIp($ip, '자동 차단: Honeypot 필드 감지 (봇)', now()->addDay());
            return response()->json([
                'success' => false,
                'message' => '요청을 처리할 수 없습니다.',
            ], 403);
        }

        // 2) 레이트 리미팅: IP당 분당 60회
        $rateLimitKey = "api_rate:{$ip}";
        $currentCount = (int) Cache::get($rateLimitKey, 0);

        if ($currentCount >= 60) {
            return response()->json([
                'success' => false,
                'message' => '너무 많은 요청입니다. 잠시 후 다시 시도하세요.',
                'retry_after' => 60,
            ], 429);
        }

        // 카운트 증가 (1분 TTL)
        if ($currentCount === 0) {
            Cache::put($rateLimitKey, 1, 60);
        } else {
            Cache::increment($rateLimitKey);
        }

        return $next($request);
    }

    /**
     * IP 자동 차단 (ip_bans 테이블에 삽입)
     */
    private function autoBanIp(string $ip, string $reason, $expiresAt = null): void
    {
        try {
            DB::table('ip_bans')->insertOrIgnore([
                'ip_address' => $ip,
                'reason'     => $reason,
                'expires_at' => $expiresAt,
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            // 캐시도 즉시 갱신
            Cache::put("ip_ban:{$ip}", [
                'banned'     => true,
                'reason'     => $reason,
                'expires_at' => $expiresAt,
            ], 300);
        } catch (\Exception $e) {
            // ip_bans 테이블이 없으면 무시
        }
    }
}
