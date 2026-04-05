<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\News;
use App\Models\NewsCategory;
use App\Models\Comment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class NewsController extends Controller
{
    /** 뉴스 목록 (카테고리 필터, 페이지네이션) */
    public function index(Request $request)
    {
        $query = News::query()->orderByDesc('published_at');

        // 메인 카테고리 필터
        if ($request->filled('main_category_id')) {
            $query->where('main_category_id', $request->main_category_id);
        }

        // 서브 카테고리 필터
        if ($request->filled('category_id')) {
            $query->where('category_id', $request->category_id);
        }

        // 이전 방식 호환: 문자열 category
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

    /** 카테고리 트리 반환 (메인 + 서브) */
    public function categories()
    {
        $mainCategories = NewsCategory::active()
            ->mainCategories()
            ->with(['children' => function ($q) {
                $q->active()->orderBy('priority');
            }])
            ->get();

        return response()->json($mainCategories);
    }

    /** 특정 카테고리별 뉴스 (slug 기반) */
    public function byCategory(Request $request, $slug)
    {
        $category = NewsCategory::where('slug', $slug)->firstOrFail();

        $query = News::orderByDesc('published_at');

        if (is_null($category->parent_id)) {
            // 메인 카테고리 → 해당 메인카테고리의 모든 뉴스
            $query->where('main_category_id', $category->id);
        } else {
            // 서브 카테고리 → 해당 서브카테고리의 뉴스
            $query->where('category_id', $category->id);
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
            'category'     => $category,
            'data'         => $news->items(),
            'current_page' => $news->currentPage(),
            'last_page'    => $news->lastPage(),
            'total'        => $news->total(),
        ]);
    }

    /** 일일 다이제스트: 최근 24시간 주요 뉴스 5개 */
    public function digest()
    {
        // is_digest=true 뉴스 우선, 없으면 최근 24시간 is_featured
        $items = News::where('is_digest', true)
            ->whereDate('published_at', today())
            ->orderByDesc('view_count')
            ->limit(5)
            ->get(['id', 'title', 'summary', 'image_url', 'published_at', 'category', 'category_id', 'main_category_id', 'source']);

        if ($items->isEmpty()) {
            $items = News::where('published_at', '>=', now()->subHours(24))
                ->orderByDesc('view_count')
                ->limit(5)
                ->get(['id', 'title', 'summary', 'image_url', 'published_at', 'category', 'category_id', 'main_category_id', 'source']);
        }

        // 어제 뉴스 요약 (카테고리별 대표 기사)
        $yesterday = now()->subDay()->toDateString();
        $yesterdayNews = News::whereDate('published_at', $yesterday)
            ->orderByDesc('view_count')
            ->limit(20)
            ->get(['id', 'title', 'summary', 'image_url', 'published_at', 'category', 'source']);

        return response()->json([
            'today'     => $items,
            'yesterday' => $yesterdayNews->take(8)->values(),
            'date'      => today()->toDateString(),
        ]);
    }

    /** 심층 기사 (is_featured=true) */
    public function featured(Request $request)
    {
        $query = News::where('is_featured', true)
            ->orderByDesc('published_at');

        if ($request->filled('main_category_id')) {
            $query->where('main_category_id', $request->main_category_id);
        }

        $perPage = $request->input('per_page', 10);
        $news = $query->paginate($perPage);

        return response()->json([
            'data'         => $news->items(),
            'current_page' => $news->currentPage(),
            'last_page'    => $news->lastPage(),
            'total'        => $news->total(),
        ]);
    }

    /** 뉴스 상세 */
    public function show($id)
    {
        $news = News::findOrFail($id);

        // 조회수 증가
        $news->increment('view_count');

        $data = $news->toArray();

        // 카테고리 정보 포함
        if ($news->category_id) {
            $data['sub_category'] = $news->subCategory;
        }
        if ($news->main_category_id) {
            $data['main_category_obj'] = $news->mainCategory;
        }

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

        // 좋아요 수
        $data['like_count'] = DB::table('content_likes')
            ->where('likeable_type', 'news')
            ->where('likeable_id', $id)
            ->count();

        // 댓글
        $data['comments'] = Comment::where('commentable_type', 'news')
            ->where('commentable_id', $id)
            ->with('user:id,name,username,avatar')
            ->latest()
            ->get();

        // 관련 뉴스 (같은 서브카테고리)
        $data['related'] = [];
        if ($news->category_id) {
            $data['related'] = News::where('category_id', $news->category_id)
                ->where('id', '!=', $id)
                ->orderByDesc('published_at')
                ->limit(5)
                ->get(['id', 'title', 'image_url', 'published_at', 'source', 'category']);
        }

        // 이전/다음 기사
        $data['prev'] = News::where('id', '<', $id)->orderByDesc('id')->first(['id', 'title']);
        $data['next'] = News::where('id', '>', $id)->orderBy('id')->first(['id', 'title']);

        return response()->json($data);
    }

    /**
     * 어제의 뉴스 요약 (홈페이지 위젯용)
     * 기존 호환성 유지
     */
    public function yesterdaySummary()
    {
        $yesterday = now()->subDay()->toDateString();

        $news = News::whereDate('published_at', $yesterday)
            ->orderByDesc('published_at')
            ->get(['id', 'title', 'summary', 'source', 'category', 'image_url', 'published_at', 'url']);

        if ($news->isEmpty()) {
            $news = News::where('published_at', '>=', now()->subHours(36))
                ->orderByDesc('published_at')
                ->get(['id', 'title', 'summary', 'source', 'category', 'image_url', 'published_at', 'url']);
        }

        $priorityOrder = ['이민/비자', '미국생활', '정치/사회', '경제', '생활', '문화', '스포츠', '기타'];
        $grouped = $news->groupBy('category');

        $result = collect();
        foreach ($priorityOrder as $cat) {
            if (isset($grouped[$cat])) {
                $result = $result->concat($grouped[$cat]->take(2));
            }
            if ($result->count() >= 8) break;
        }

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

        $todayCount = Comment::where('user_id', Auth::id())->whereDate('created_at', today())->count();
        if ($todayCount <= 10) {
            Auth::user()->addPoints(5, 'comment_write', 'earn', $comment->id, '댓글 작성');
        }

        return response()->json([
            'message' => '댓글이 등록되었습니다.',
            'comment' => $comment->load('user:id,name,username,avatar'),
        ], 201);
    }
}
