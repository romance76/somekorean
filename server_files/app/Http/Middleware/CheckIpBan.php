<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\Response;

class CheckIpBan
{
    public function handle(Request $request, Closure $next): Response
    {
        $ip = $request->ip();

        try {
            $banned = DB::table('ip_bans')
                ->where('ip_address', $ip)
                ->where(function ($q) {
                    $q->whereNull('expires_at')
                      ->orWhere('expires_at', '>', now());
                })
                ->exists();

            if ($banned) {
                return response()->json(['error' => '접근이 차단되었습니다.'], 403);
            }
        } catch (\Exception $e) {
            // ip_bans 테이블이 없으면 무시
        }

        return $next($request);
    }
}
