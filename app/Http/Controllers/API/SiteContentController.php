<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

/**
 * 공개 사이트 콘텐츠 API (Phase 2-C 묶음 5).
 * Footer 링크·정적 페이지·FAQ 공개 조회.
 */
class SiteContentController extends Controller
{
    public function footerLinks()
    {
        $links = Cache::remember('site.footer_links', 300, function () {
            return DB::table('footer_links')
                ->where('enabled', true)
                ->orderBy('section')->orderBy('sort_order')
                ->get()
                ->groupBy('section');
        });
        return response()->json(['success' => true, 'data' => $links]);
    }

    public function staticPage(string $slug)
    {
        $page = Cache::remember("site.static_page.{$slug}", 300, function () use ($slug) {
            return DB::table('static_pages')->where('slug', $slug)->where('published', true)->first();
        });
        if (!$page) return response()->json(['success' => false, 'message' => 'Not found'], 404);
        return response()->json(['success' => true, 'data' => $page]);
    }

    public function faqs(Request $request)
    {
        $category = $request->query('category');
        $cacheKey = 'site.faqs.' . ($category ?: 'all');
        $items = Cache::remember($cacheKey, 300, function () use ($category) {
            $q = DB::table('faqs')->where('published', true);
            if ($category) $q->where('category', $category);
            return $q->orderBy('category')->orderBy('sort_order')->get();
        });
        return response()->json(['success' => true, 'data' => $items]);
    }

    public function faqHelpful($id)
    {
        DB::table('faqs')->where('id', $id)->increment('helpful_count');
        Cache::forget('site.faqs.all');
        return response()->json(['success' => true]);
    }
}
