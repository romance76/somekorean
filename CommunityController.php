<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Models\PostLike;
use App\Models\Comment;
use App\Models\Board;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class CommunityController extends Controller
{
    private $categories = [
        ['slug'=>'free','name'=>'자유게시판','icon'=>'💬','description'=>'일상·수다·정보공유'],
        ['slug'=>'anonymous','name'=>'익명게시판','icon'=>'🎭','description'=>'실명 없이 자유롭게'],
        ['slug'=>'humor','name'=>'유머·짤','icon'=>'😂','description'=>'웃긴 글·짤방'],
        ['slug'=>'vent','name'=>'속풀이','icon'=>'😤','description'=>'고민상담·감정 토로'],
        ['slug'=>'cooking','name'=>'요리·레시피','icon'=>'🍳','description'=>'한식·미국 요리'],
        ['slug'=>'shopping','name'=>'쇼핑·핫딜','icon'=>'🛍️','description'=>'미국 핫딜·할인 정보'],
        ['slug'=>'parenting','name'=>'육아·교육','icon'=>'👶','description'=>'자녀 양육·학교'],
        ['slug'=>'beauty','name'=>'뷰티·패션','icon'=>'💄','description'=>'화장품·스킨케어·패션'],
        ['slug'=>'travel','name'=>'여행·맛집','icon'=>'✈️','description'=>'미국 여행·한인 맛집'],
        ['slug'=>'news_talk','name'=>'뉴스·시사','icon'=>'📰','description'=>'미국·한국 뉴스'],
        ['slug'=>'local_atlanta','name'=>'애틀란타','icon'=>'🍑','description'=>'조지아·수와니·둘루스'],
        ['slug'=>'local_la','name'=>'로스앤젤레스','icon'=>'🌴','description'=>'LA·OC·샌디에고'],
        ['slug'=>'local_ny','name'=>'뉴욕·뉴저지','icon'=>'🗽','description'=>'NY·NJ·보스턴'],
        ['slug'=>'local_dallas','name'=>'달라스·휴스턴','icon'=>'🤠','description'=>'텍사스 한인'],
        ['slug'=>'local_seattle','name'=>'시애틀·시카고','icon'=>'🌧️','description'=>'북서부·중부'],
    ];

    /**
     * 카테고리 목록 반환
     */
    public function categories()
    {
        return response()->json($this->categories);
    }

    /**
     * 카테고리별 게시글 목록
     */
    public function posts($slug)
    {
        $validSlugs = array_column($this->categories, 'slug');
        if (!in_array($slug, $validSlugs)) {
            return response()->json(['message' => '유효하지 않은 카테고리입니다.'], 404);
        }

        $board = Board::firstOrCreate(
            ['slug' => $slug],
            ['name' => collect($this->categories)->firstWhere('slug', $slug)['name'], 'category' => 'community', 'is_active' => true]
        );

        $sort = request('sort', 'latest');

        $query = Post::with(['user:id,nickname,username,avatar'])
            ->where('board_id', $board->id)
            ->where('status', 'active');

        if ($sort === 'popular') {
            $query->orderByDesc('like_count')->orderByDesc('view_count');
        } else {
            $query->orderByDesc('created_at');
        }

        $posts = $query->paginate(20);

        // 익명 처리
        $posts->getCollection()->transform(function ($post) {
            if ($post->is_anonymous) {
                $post->user = (object)['id' => 0, 'nickname' => '익명', 'username' => 'anonymous', 'avatar' => null];
            }
            return $post;
        });

        return response()->json($posts);
    }

    /**
     * 글 상세 보기
     */
    public function show($id)
    {
        $post = Post::with([
            'user:id,nickname,username,avatar',
            'comments' => function ($q) {
                $q->whereNull('parent_id')
                  ->where('status', 'active')
                  ->with(['user:id,nickname,username,avatar', 'replies' => function ($r) {
                      $r->where('status', 'active')->with('user:id,nickname,username,avatar')->orderBy('created_at');
                  }])
                  ->orderByDesc('created_at');
            },
        ])->findOrFail($id);

        $post->increment('view_count');

        // 익명 처리
        if ($post->is_anonymous) {
            $post->user = (object)['id' => 0, 'nickname' => '익명', 'username' => 'anonymous', 'avatar' => null];
        }

        // 댓글 익명 처리
        $post->comments->transform(function ($comment) {
            if ($comment->is_anonymous) {
                $comment->user = (object)['id' => 0, 'nickname' => '익명', 'username' => 'anonymous', 'avatar' => null];
            }
            if ($comment->replies) {
                $comment->replies->transform(function ($reply) {
                    if ($reply->is_anonymous) {
                        $reply->user = (object)['id' => 0, 'nickname' => '익명', 'username' => 'anonymous', 'avatar' => null];
                    }
                    return $reply;
                });
            }
            return $comment;
        });

        // 로그인 유저의 좋아요 여부
        $post->is_liked = false;
        if (Auth::check()) {
            $post->is_liked = PostLike::where('post_id', $id)->where('user_id', Auth::id())->exists();
        }

        return response()->json($post);
    }

    /**
     * 글 작성
     */
    public function store(Request $request)
    {
        $request->validate([
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'category_slug' => 'required|string',
            'is_anonymous' => 'boolean',
        ]);

        $validSlugs = array_column($this->categories, 'slug');
        if (!in_array($request->category_slug, $validSlugs)) {
            return response()->json(['message' => '유효하지 않은 카테고리입니다.'], 422);
        }

        $board = Board::firstOrCreate(
            ['slug' => $request->category_slug],
            ['name' => collect($this->categories)->firstWhere('slug', $request->category_slug)['name'], 'category' => 'community', 'is_active' => true]
        );

        $post = Post::create([
            'board_id' => $board->id,
            'user_id' => Auth::id(),
            'title' => $request->title,
            'content' => $request->content,
            'is_anonymous' => $request->is_anonymous ?? false,
            'images' => $request->images,
            'thumbnail' => $request->thumbnail,
        ]);

        return response()->json($post->load('user:id,nickname,username,avatar'), 201);
    }

    /**
     * 글 수정 (본인만)
     */
    public function update(Request $request, $id)
    {
        $post = Post::findOrFail($id);

        if ($post->user_id !== Auth::id()) {
            return response()->json(['message' => '권한이 없습니다.'], 403);
        }

        $validated = $request->validate([
            'title' => 'sometimes|required|string|max:255',
            'content' => 'sometimes|required|string',
        ]);

        $post->update($validated);
        return response()->json($post);
    }

    /**
     * 글 삭제 (본인 또는 admin)
     */
    public function destroy($id)
    {
        $post = Post::findOrFail($id);

        if ($post->user_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '권한이 없습니다.'], 403);
        }

        $post->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }

    /**
     * 좋아요 토글
     */
    public function like($id)
    {
        $post = Post::findOrFail($id);
        $existing = PostLike::where('post_id', $id)->where('user_id', Auth::id())->first();

        if ($existing) {
            $existing->delete();
            $post->decrement('like_count');
            return response()->json(['liked' => false, 'like_count' => $post->fresh()->like_count]);
        } else {
            PostLike::create(['post_id' => $id, 'user_id' => Auth::id()]);
            $post->increment('like_count');
            return response()->json(['liked' => true, 'like_count' => $post->fresh()->like_count]);
        }
    }

    /**
     * 댓글 목록
     */
    public function comments($postId)
    {
        $comments = Comment::where('post_id', $postId)
            ->whereNull('parent_id')
            ->where('status', 'active')
            ->with(['user:id,nickname,username,avatar', 'replies' => function ($q) {
                $q->where('status', 'active')->with('user:id,nickname,username,avatar')->orderBy('created_at');
            }])
            ->orderByDesc('created_at')
            ->get();

        // 익명 처리
        $comments->transform(function ($comment) {
            if ($comment->is_anonymous) {
                $comment->user = (object)['id' => 0, 'nickname' => '익명', 'username' => 'anonymous', 'avatar' => null];
            }
            if ($comment->replies) {
                $comment->replies->transform(function ($reply) {
                    if ($reply->is_anonymous) {
                        $reply->user = (object)['id' => 0, 'nickname' => '익명', 'username' => 'anonymous', 'avatar' => null];
                    }
                    return $reply;
                });
            }
            return $comment;
        });

        return response()->json($comments);
    }

    /**
     * 댓글 작성
     */
    public function storeComment(Request $request, $postId)
    {
        $request->validate([
            'content' => 'required|string|max:2000',
            'parent_id' => 'nullable|exists:comments,id',
            'is_anonymous' => 'boolean',
        ]);

        $post = Post::findOrFail($postId);

        $comment = Comment::create([
            'post_id' => $postId,
            'user_id' => Auth::id(),
            'content' => $request->content,
            'parent_id' => $request->parent_id,
            'is_anonymous' => $request->is_anonymous ?? false,
        ]);

        $post->increment('comment_count');

        return response()->json($comment->load('user:id,nickname,username,avatar'), 201);
    }

    /**
     * 댓글 삭제
     */
    public function destroyComment($id)
    {
        $comment = Comment::findOrFail($id);

        if ($comment->user_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '권한이 없습니다.'], 403);
        }

        $post = Post::find($comment->post_id);
        $comment->delete();
        if ($post) {
            $post->decrement('comment_count');
        }

        return response()->json(['message' => '댓글이 삭제되었습니다.']);
    }
}
