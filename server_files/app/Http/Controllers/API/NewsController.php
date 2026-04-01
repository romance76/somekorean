<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\News;
use App\Models\Comment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class NewsController extends Controller
{
    public function index(Request $request)
    {
        $query = News::query()->orderByDesc('published_at');

        if ($request->filled('category') && $request->category !== '전체') {
            $query->where('category', $request->category);
        }

        if ($request->filled('source')) {
            $query->where('source', $request->source);
        }

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                  ->orWhere('summary', 'like', "%{$search}%");
            });
        }

        $perPage = $request->input('per_page', 20);
        $news = $query->paginate($perPage);

        return response()->json([
            'data'         => $news->items(),
            'current_page' => $news->currentPage(),
            'last_page'    => $news->lastPage(),
            'total'        => $news->total(),
        ]);
    }

    public function show($id)
    {
        $news = News::findOrFail($id);
        $data = $news->toArray();

        // 로그인 사용자 좋아요 여부
        if (Auth::check()) {
            $data['is_liked'] = DB::table('content_likes')
                ->where('user_id', Auth::id())
                ->where('likeable_type', 'news')
                ->where('likeable_id', $id)
                ->exists();
        } else {
            $data['is_liked'] = false;
        }

        // 좋아요 수 (content_likes 테이블에서 집계)
        $data['like_count'] = DB::table('content_likes')
            ->where('likeable_type', 'news')
            ->where('likeable_id', $id)
            ->count();

        // 댓글 불러오기
        $data['comments'] = Comment::where('commentable_type', 'news')
            ->where('commentable_id', $id)
            ->with('user:id,name,username,avatar')
            ->latest()
            ->get();

        return response()->json($data);
    }

    /**
     * 어제의 뉴스 요약 (홈페이지 위젯용)
     * 전날 뉴스를 카테고리별로 대표 기사 1~2건씩, 최대 8건 반환
     */
    public function yesterdaySummary()
    {
        $yesterday = now()->subDay()->toDateString();

        // 전날 뉴스 먼저 시도
        $news = News::whereDate('published_at', $yesterday)
            ->orderByDesc('published_at')
            ->get(['id', 'title', 'summary', 'source', 'category', 'image_url', 'published_at', 'url']);

        // 전날 뉴스가 없으면 최근 24시간
        if ($news->isEmpty()) {
            $news = News::where('published_at', '>=', now()->subHours(36))
                ->orderByDesc('published_at')
                ->get(['id', 'title', 'summary', 'source', 'category', 'image_url', 'published_at', 'url']);
        }

        // 카테고리별로 대표 기사 추출 (이민/비자 우선)
        $priorityOrder = ['이민/비자', '미국생활', '정치/사회', '경제', '생활', '문화', '스포츠', '기타'];
        $grouped = $news->groupBy('category');

        $result = collect();
        foreach ($priorityOrder as $cat) {
            if (isset($grouped[$cat])) {
                $result = $result->concat($grouped[$cat]->take(2));
            }
            if ($result->count() >= 8) break;
        }

        // 8건 미만이면 나머지 채우기
        if ($result->count() < 8) {
            $existing = $result->pluck('id');
            $more = $news->whereNotIn('id', $existing)->take(8 - $result->count());
            $result = $result->concat($more);
        }

        return response()->json([
            'date'  => $yesterday,
            'total' => $news->count(),
            'items' => $result->take(8)->values(),
        ]);
    }

    /** 좋아요 토글 */
    public function like($id)
    {
        News::findOrFail($id);
        $userId = Auth::id();

        $existing = DB::table('content_likes')
            ->where('user_id', $userId)
            ->where('likeable_type', 'news')
            ->where('likeable_id', $id)
            ->first();

        if ($existing) {
            DB::table('content_likes')->where('id', $existing->id)->delete();
        } else {
            DB::table('content_likes')->insert([
                'user_id'       => $userId,
                'likeable_type' => 'news',
                'likeable_id'   => $id,
                'created_at'    => now(),
            ]);
        }

        $likeCount = DB::table('content_likes')
            ->where('likeable_type', 'news')
            ->where('likeable_id', $id)
            ->count();

        return response()->json(['liked' => !$existing, 'like_count' => $likeCount]);
    }

    /** 댓글 작성 */
    public function comment(Request $request, $id)
    {
        News::findOrFail($id);
        $request->validate(['content' => 'required|string|max:2000']);

        $comment = Comment::create([
            'post_id'          => null,
            'commentable_type' => 'news',
            'commentable_id'   => $id,
            'user_id'          => Auth::id(),
            'content'          => $request->content,
        ]);

        // 포인트 지급
        $todayCount = Comment::where('user_id', Auth::id())->whereDate('created_at', today())->count();
        if ($todayCount <= 10) {
            Auth::user()->addPoints(5, 'comment', 'earn', $comment->id, '댓글 작성');
        }

        return response()->json([
            'message' => '댓글이 등록되었습니다.',
            'comment' => $comment->load('user:id,name,username,avatar'),
        ], 201);
    }
}
