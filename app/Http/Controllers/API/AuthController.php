<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Tymon\JWTAuth\Facades\JWTAuth;
use Illuminate\Support\Str;

class AuthController extends Controller
{
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name'     => 'required|string|max:50',
            'username' => 'required|string|max:30|unique:users|alpha_dash',
            'email'    => 'required|email|unique:users',
            'password' => 'required|string|min:8|confirmed',
        ]);
        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $user = User::create([
            'name'     => $request->name,
            'username' => $request->username,
            'email'    => $request->email,
            'password' => $request->password,
            'lang'     => $request->lang ?? 'ko',
        ]);

        // 가입 포인트는 없음 (이메일 인증 후)
        $token = JWTAuth::fromUser($user);

        return response()->json([
            'message' => '회원가입이 완료되었습니다. 이메일 인증을 해주세요.',
            'token'   => $token,
            'user'    => $this->userResource($user),
        ], 201);
    }

    public function login(Request $request)
    {
        $credentials = $request->only('email', 'password');
        if (!$token = JWTAuth::attempt($credentials)) {
            return response()->json(['message' => '이메일 또는 비밀번호가 올바르지 않습니다.'], 401);
        }
        $user = JWTAuth::user();
        if ($user->status === 'banned') {
            return response()->json(['message' => '정지된 계정입니다.'], 403);
        }
        $user->update(['last_login_at' => now()]);
        return response()->json(['token' => $token, 'user' => $this->userResource($user)]);
    }

    public function logout()
    {
        JWTAuth::invalidate(JWTAuth::getToken());
        return response()->json(['message' => '로그아웃되었습니다.']);
    }

    public function refresh()
    {
        try {
            $token = JWTAuth::refresh(JWTAuth::getToken());
            return response()->json(['token' => $token]);
        } catch (\Exception $e) {
            return response()->json(['message' => '토큰 갱신 실패'], 401);
        }
    }

    public function me()
    {
        return response()->json(['user' => $this->userResource(JWTAuth::user())]);
    }

    private function userResource(User $user): array
    {
        return [
            'id'        => $user->id,
            'name'      => $user->name,
            'username'  => $user->username,
            'email'     => $user->email,
            'avatar'    => $user->avatar ? asset('storage/' . $user->avatar) : null,
            'level'     => $user->level,
            'points'    => $user->points_total,
            'cash'      => $user->cash_balance,
            'region'    => $user->region,
            'is_admin'  => $user->is_admin,
            'verified'  => !is_null($user->email_verified_at),
            'lang'      => $user->lang,
        ];
    }
}
