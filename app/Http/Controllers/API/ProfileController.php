<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\Rule;

class ProfileController extends Controller
{
    /**
     * GET /api/users/{id}
     * Public user profile with stats.
     */
    public function show($id)
    {
        $user = User::where('id', $id)
            ->where('status', 'active')
            ->firstOrFail();

        return response()->json([
            'success' => true,
            'data'    => [
                'id'            => $user->id,
                'name'          => $user->name,
                'nickname'      => $user->nickname,
                'avatar'        => $user->avatar ? asset('storage/' . $user->avatar) : null,
                'bio'           => $user->bio,
                'level'         => $user->level ?? '씨앗',
                'points'        => $user->points_total ?? 0,
                'city'          => $user->city,
                'state'         => $user->state,
                'joined'        => $user->created_at?->format('Y-m'),
                'post_count'    => $user->posts()->where('status', 'active')->count(),
                'comment_count' => $user->comments()->where('status', 'active')->count(),
            ],
        ]);
    }

    /**
     * PUT /api/user/profile
     * Update own profile.
     */
    public function update(Request $request)
    {
        $user = auth()->user();

        $request->validate([
            'name'      => 'sometimes|string|max:50',
            'nickname'  => 'nullable|string|max:50',
            'bio'       => 'nullable|string|max:500',
            'phone'     => 'nullable|string|max:20',
            'city'      => 'nullable|string|max:100',
            'state'     => 'nullable|string|max:50',
            'zip_code'  => 'nullable|string|max:20',
            'lang'      => 'nullable|in:ko,en,both',
        ]);

        $data = $request->only([
            'name', 'nickname', 'bio', 'phone',
            'city', 'state', 'zip_code', 'lang',
        ]);

        $user->update($data);

        return response()->json([
            'success' => true,
            'message' => '프로필이 수정되었습니다.',
            'data'    => $user->fresh()->makeHidden(['password', 'remember_token']),
        ]);
    }

    /**
     * POST /api/user/avatar
     * Upload avatar image.
     */
    public function uploadAvatar(Request $request)
    {
        $request->validate([
            'avatar' => 'required|image|max:3072',
        ]);

        $user = auth()->user();

        // Delete old avatar
        if ($user->avatar) {
            Storage::disk('public')->delete($user->avatar);
        }

        $path = $request->file('avatar')->store('avatars', 'public');
        $user->update(['avatar' => $path]);

        return response()->json([
            'success' => true,
            'message' => '프로필 사진이 변경되었습니다.',
            'data'    => ['avatar' => asset('storage/' . $path)],
        ]);
    }

    /**
     * GET /api/users/{id}/posts
     * Get a user's posts across all boards.
     */
    public function posts($id)
    {
        $user = User::findOrFail($id);

        $posts = Post::with('board:id,name,slug')
            ->where('user_id', $user->id)
            ->where('status', 'active')
            ->orderByDesc('created_at')
            ->paginate(20);

        return response()->json([
            'success' => true,
            'data'    => $posts,
        ]);
    }
}
