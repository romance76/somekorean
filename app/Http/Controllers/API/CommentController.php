<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class CommentController extends Controller
{
    public function store(Request $request, Post $post)
    {
        $request->validate(['content' => 'required|string|max:2000']);
        $comment = Comment::create([
            'post_id'      => $post->id,
            'user_id'      => Auth::id(),
            'parent_id'    => $request->parent_id,
            'content'      => $request->content,
            'is_anonymous' => $request->is_anonymous ?? false,
        ]);
        $post->increment('comment_count');
        // 포인트 지급 (하루 최대 50P = 10개)
        $todayComments = Comment::where('user_id', Auth::id())
            ->whereDate('created_at', today())->count();
        if ($todayComments <= 10) {
            Auth::user()->addPoints(5, 'comment', 'earn', $comment->id, '댓글 작성');
        }
        return response()->json(['message' => '댓글이 등록되었습니다.', 'comment' => $comment->load('user:id,name,username,avatar')], 201);
    }

    public function destroy(Comment $comment)
    {
        if ($comment->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        $comment->post->decrement('comment_count');
        $comment->update(['status' => 'deleted']);
        $comment->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }
}
