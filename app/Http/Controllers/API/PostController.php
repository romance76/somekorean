<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Board;
use App\Models\Post;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Validator;

class PostController extends Controller
{
    public function index(Request $request)
    {
        $query = Post::with(['user:id,name,username,avatar,level', 'board:id,name,slug'])
            ->where('status', 'active');

        if ($request->board) {
            $board = Board::where('slug', $request->board)->first();
            if ($board) $query->where('board_id', $board->id);
        }
        if ($request->search) {
            $query->where(function($q) use ($request) {
                $q->where('title', 'like', '%'.$request->search.'%')
                  ->orWhere('content', 'like', '%'.$request->search.'%');
            });
        }

        $posts = $query->orderByDesc('is_pinned')
                       ->orderByDesc('created_at')
                       ->paginate(20);

        return response()->json($posts);
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'board_id' => 'required|exists:boards,id',
            'title'    => 'required|string|max:200',
            'content'  => 'required|string',
        ]);
        if ($validator->fails()) return response()->json(['errors' => $validator->errors()], 422);

        $post = Post::create([
            'board_id'     => $request->board_id,
            'user_id'      => Auth::id(),
            'title'        => $request->title,
            'content'      => $request->content,
            'is_anonymous' => $request->is_anonymous ?? false,
        ]);

        // 포인트 지급
        Auth::user()->addPoints(30, 'post', 'earn', $post->id, '게시글 작성');

        return response()->json(['message' => '게시글이 등록되었습니다.', 'post' => $post->load('user', 'board')], 201);
    }

    public function show(Post $post)
    {
        if ($post->status !== 'active') abort(404);
        $post->increment('view_count');
        $post->load(['user:id,name,username,avatar,level', 'board:id,name,slug', 'comments.user:id,name,username,avatar']);
        $post->is_liked = $post->isLikedBy(Auth::user());
        return response()->json($post);
    }

    public function update(Request $request, Post $post)
    {
        if ($post->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        $post->update($request->only(['title', 'content']));
        return response()->json(['message' => '수정되었습니다.', 'post' => $post]);
    }

    public function destroy(Post $post)
    {
        if ($post->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        $post->update(['status' => 'deleted']);
        $post->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }

    public function like(Post $post)
    {
        $user = Auth::user();
        $existing = $post->likes()->where('user_id', $user->id)->first();
        if ($existing) {
            $existing->delete();
            $post->decrement('like_count');
            return response()->json(['liked' => false, 'like_count' => $post->like_count]);
        }
        $post->likes()->create(['user_id' => $user->id]);
        $post->increment('like_count');
        // 작성자에게 포인트
        if ($post->user_id !== $user->id) {
            $post->user->addPoints(10, 'like_received', 'earn', $post->id, '추천 받음');
        }
        return response()->json(['liked' => true, 'like_count' => $post->fresh()->like_count]);
    }
}
