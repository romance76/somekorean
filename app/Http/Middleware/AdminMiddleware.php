<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AdminMiddleware
{
    /**
     * 관리자 권한 체크 미들웨어
     * - 인증된 사용자의 role이 'admin'인지 확인
     * - 미인증 또는 비관리자: 403 JSON 응답
     */
    public function handle(Request $request, Closure $next): Response
    {
        $user = $request->user();

        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => '인증이 필요합니다.',
            ], 401);
        }

        if (!in_array($user->role, ['admin', 'super_admin', 'moderator'])) {
            return response()->json([
                'success' => false,
                'message' => '관리자 권한이 필요합니다.',
            ], 403);
        }

        return $next($request);
    }
}
