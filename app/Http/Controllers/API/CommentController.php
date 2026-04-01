<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

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

        // 원글 작성자에게 알림 (자신의 글에 댓글 달면 알림 안 보냄)
        if ($post->user_id && $post->user_id !== Auth::id()) {
            DB::table('notifications')->insert([
                'user_id'    => $post->user_id,
                'type'       => 'comment',
                'title'      => '새 댓글이 달렸습니다',
                'body'       => Auth::user()->name . '님이 댓글을 남겼습니다: ' . mb_substr($request->content, 0, 50),
                'data'       => json_encode(['post_id' => $post->id, 'comment_id' => $comment->id]),
                'url'        => '/board/' . $post->id,
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }

        // 답글 시 부모 댓글 작성자에게 알림
        if ($request->parent_id) {
            $parent = Comment::find($request->parent_id);
            if ($parent && $parent->user_id !== Auth::id() && $parent->user_id !== $post->user_id) {
                try {
                    DB::table('notifications')->insert([
                        'user_id'    => $parent->user_id,
                        'type'       => 'reply',
                        'title'      => Auth::user()->name . '님이 댓글에 답글을 달았습니다',
                        'body'       => mb_substr($request->content, 0, 50),
                        'data'       => json_encode(['post_id' => $post->id, 'comment_id' => $comment->id]),
                        'url'        => '/community/post/' . $post->id,
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                } catch (\Exception $e) {}
            }
        }

        $todayComments = Comment::where('user_id', Auth::id())
            ->whereDate('created_at', today())->count();
        if ($todayComments <= 10) {
            Auth::user()->addPoints(5, 'comment_write', 'earn', $comment->id, '댓글 작성');
        }
        return response()->json(['message' => '댓글이 등록되었습니다.', 'comment' => $comment->load('user:id,name,username,avatar')], 201);
    }

    public function update(Request $request, Comment $comment)
    {
        if ($comment->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        $request->validate(['content' => 'required|string|max:2000']);
        $comment->update(['content' => $request->content]);
        return response()->json(['message' => '댓글이 수정되었습니다.', 'comment' => $comment->load('user:id,name,username,avatar')]);
    }

    public function destroy(Comment $comment)
    {
        if ($comment->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        if ($comment->post_id && $comment->post) {
            $comment->post->decrement('comment_count');
        }
        $comment->update(['status' => 'deleted']);
        $comment->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }
}
