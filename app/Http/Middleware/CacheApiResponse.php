<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;

/**
 * GET API 응답을 Redis에 캐싱하는 미들웨어.
 * 사이드바, 배너 등 자주 호출되지만 변동이 적은 API에 적용.
 */
class CacheApiResponse
{
    public function handle(Request $request, Closure $next, $ttl = 300)
    {
        // GET 요청만 캐싱
        if ($request->method() !== 'GET') return $next($request);

        // 검색/위치 요청은 캐싱하지 않음 (결과가 매번 다름)
        if ($request->search || $request->lat || $request->lng) return $next($request);

        $cacheKey = 'api_cache_' . md5($request->fullUrl());
        $cached = Cache::get($cacheKey);

        if ($cached) {
            return response()->json($cached);
        }

        $response = $next($request);

        // 200 OK일 때만 캐싱
        if ($response->getStatusCode() === 200) {
            $data = json_decode($response->getContent(), true);
            if ($data) {
                Cache::put($cacheKey, $data, (int) $ttl);
            }
        }

        return $response;
    }
}
