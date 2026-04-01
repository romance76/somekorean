<?php

namespace App\Http\Controllers\API;

use App\Events\WebRTCSignal;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Str;

class CallController extends Controller
{
    // 통화 요청 / SDP 전달 / ICE 전달 / 통화 종료 모두 이 엔드포인트로 처리
    public function signal(Request $request)
    {
        $request->validate([
            'type'        => 'required|in:call-request,call-end,offer,answer,ice-candidate',
            'to_user_id'  => 'required|integer',
            'call_id'     => 'nullable|string',
            'payload'     => 'nullable|array',
        ]);

        $callId = $request->call_id ?? Str::uuid()->toString();

        broadcast(new WebRTCSignal(
            type:       $request->type,
            payload:    $request->payload ?? [],
            fromUserId: Auth::id(),
            toUserId:   $request->to_user_id,
            callId:     $callId,
        ));

        return response()->json(['call_id' => $callId]);
    }
}
