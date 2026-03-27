<?php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Tymon\JWTAuth\Facades\JWTAuth;

class AdminMiddleware
{
    public function handle(Request $request, Closure $next)
    {
        try {
            $user = JWTAuth::parseToken()->authenticate();
            if (!$user || !$user->is_admin) {
                return response()->json(['message' => '관리자 권한이 필요합니다.'], 403);
            }
        } catch (\Exception $e) {
            return response()->json(['message' => '인증이 필요합니다.'], 401);
        }
        return $next($request);
    }
}
