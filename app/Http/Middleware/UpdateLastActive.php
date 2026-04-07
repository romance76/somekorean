<?php
namespace App\Http\Middleware;
use Closure;
use Illuminate\Http\Request;

class UpdateLastActive
{
    public function handle(Request $request, Closure $next)
    {
        if ($user = $request->user()) {
            // 5분마다만 업데이트 (성능)
            if (!$user->last_active_at || now()->diffInMinutes($user->last_active_at) >= 5) {
                $user->timestamps = false;
                $user->update(['last_active_at' => now()]);
            }
        }
        return $next($request);
    }
}
