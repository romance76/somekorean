<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Models\Business;
use App\Models\JobPost;
use App\Models\MarketItem;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;

class AIController extends Controller
{
    private function openai(string $prompt, int $maxTokens = 500): ?string
    {
        $key = config('services.openai.key');
        if (!$key) return null;

        $res = Http::withToken($key)
            ->timeout(20)
            ->post('https://api.openai.com/v1/chat/completions', [
                'model'       => 'gpt-3.5-turbo',
                'max_tokens'  => $maxTokens,
                'temperature' => 0.3,
                'messages'    => [['role' => 'user', 'content' => $prompt]],
            ]);

        return $res->json('choices.0.message.content');
    }

    // ── AI 검색 ──────────────────────────────────────────────────
    public function search(Request $request)
    {
        $request->validate(['q' => 'required|string|max:200']);
        $q = trim($request->q);

        $cacheKey = 'ai_search:' . md5($q);
        return Cache::remember($cacheKey, 300, function () use ($q) {
            // GPT에게 검색 키워드 분석 요청
            $analysis = $this->openai(
                "사용자 검색어: \"{$q}\"\n" .
                "다음 JSON으로 분석해줘 (한국어/영어 혼용 가능):\n" .
                "{\"keywords\":[\"단어1\",\"단어2\"],\"category\":\"posts|jobs|market|businesses\",\"location\":\"도시명 or null\"}\n" .
                "JSON만 반환. 설명 없이."
            );

            $parsed = null;
            if ($analysis) {
                $json = preg_replace('/```json?|```/', '', $analysis);
                $parsed = json_decode(trim($json), true);
            }

            $keywords = $parsed['keywords'] ?? [$q];
            $category = $parsed['category'] ?? 'posts';
            $location = $parsed['location'] ?? null;

            $results = [];

            // 게시글 검색
            $postQ = Post::with('user:id,name,username,avatar')
                ->select('id', 'title', 'content', 'user_id', 'created_at', 'views_count', 'likes_count');
            foreach ($keywords as $kw) {
                $postQ->orWhere('title', 'like', "%{$kw}%")
                      ->orWhere('content', 'like', "%{$kw}%");
            }
            if ($location) $postQ->orWhere('content', 'like', "%{$location}%");
            $results['posts'] = $postQ->latest()->limit(10)->get();

            // 업소 검색
            $bizQ = Business::select('id', 'name', 'description', 'category', 'city', 'address');
            foreach ($keywords as $kw) {
                $bizQ->orWhere('name', 'like', "%{$kw}%")
                     ->orWhere('description', 'like', "%{$kw}%")
                     ->orWhere('category', 'like', "%{$kw}%");
            }
            if ($location) $bizQ->orWhere('city', 'like', "%{$location}%");
            $results['businesses'] = $bizQ->limit(6)->get();

            // 구인구직
            $jobQ = JobPost::select('id', 'title', 'description', 'salary', 'location', 'created_at');
            foreach ($keywords as $kw) {
                $jobQ->orWhere('title', 'like', "%{$kw}%")
                     ->orWhere('description', 'like', "%{$kw}%");
            }
            $results['jobs'] = $jobQ->latest()->limit(6)->get();

            // 중고장터
            $mktQ = MarketItem::select('id', 'title', 'price', 'description', 'status', 'created_at');
            foreach ($keywords as $kw) {
                $mktQ->orWhere('title', 'like', "%{$kw}%")
                     ->orWhere('description', 'like', "%{$kw}%");
            }
            $results['market'] = $mktQ->latest()->limit(6)->get();

            return response()->json([
                'query'    => $q,
                'ai_note'  => $analysis ? '✨ AI가 검색어를 분석했습니다' : null,
                'keywords' => $keywords,
                'results'  => $results,
            ]);
        });
    }

    // ── AI 번역 ──────────────────────────────────────────────────
    public function translate(Request $request)
    {
        $request->validate([
            'text'   => 'required|string|max:2000',
            'target' => 'required|in:ko,en,es',
        ]);

        $langMap = ['ko' => '한국어', 'en' => 'English', 'es' => 'Español'];
        $targetLang = $langMap[$request->target];

        $cacheKey = 'translate:' . md5($request->text . $request->target);
        $translated = Cache::remember($cacheKey, 3600, function () use ($request, $targetLang) {
            $result = $this->openai(
                "다음 텍스트를 {$targetLang}로 번역해줘. 번역문만 반환. 설명 없이:\n\n{$request->text}",
                800
            );
            return $result ?? $request->text;
        });

        return response()->json(['translated' => $translated]);
    }

    // ── 추천 피드 ────────────────────────────────────────────────
    public function feed(Request $request)
    {
        $userId   = Auth::id();
        $perPage  = 20;

        // 비로그인: 최신 인기글
        if (!$userId) {
            $posts = Post::with('user:id,name,username,avatar')
                ->withCount(['likes', 'comments'])
                ->latest()->paginate($perPage);
            return response()->json($posts);
        }

        // 관심사 기반 추천
        // 1) 사용자가 좋아요 한 게시글의 카테고리/태그 수집
        $likedBoardIds = DB::table('post_likes')
            ->join('posts', 'posts.id', '=', 'post_likes.post_id')
            ->where('post_likes.user_id', $userId)
            ->pluck('posts.board_id')
            ->countBy()
            ->sortDesc()
            ->keys()
            ->take(5)
            ->toArray();

        // 2) 같은 도시/지역
        $userCity = DB::table('users')->where('id', $userId)->value('city');

        // 3) 최근 7일 인기글 (조회+좋아요 기준)
        $query = Post::with('user:id,name,username,avatar')
            ->withCount(['likes', 'comments'])
            ->where('created_at', '>=', now()->subDays(30));

        if ($likedBoardIds) {
            $query->orderByRaw(
                'CASE WHEN board_id IN (' . implode(',', array_map('intval', $likedBoardIds)) . ') THEN 2 ELSE 0 END DESC'
            );
        }

        $posts = $query->orderByRaw('(views_count * 0.3 + likes_count * 0.7) DESC')
            ->paginate($perPage);

        return response()->json($posts);
    }
}
