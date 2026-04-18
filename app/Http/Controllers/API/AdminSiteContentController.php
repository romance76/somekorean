<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

/**
 * 관리자 사이트 콘텐츠 CRUD (Phase 2-C 묶음 5).
 * Footer/StaticPages/FAQ + 설정 변경 이력.
 */
class AdminSiteContentController extends Controller
{
    // ─── Footer ───
    public function footerLinks() {
        return response()->json([
            'success' => true,
            'data' => DB::table('footer_links')->orderBy('section')->orderBy('sort_order')->get(),
        ]);
    }

    public function footerLinkStore(Request $request) {
        $data = $request->validate([
            'section'    => 'required|string|max:100',
            'label'      => 'required|string|max:255',
            'label_en'   => 'nullable|string|max:255',
            'route_path' => 'required|string|max:255',
            'icon'       => 'nullable|string|max:50',
            'sort_order' => 'integer',
            'enabled'    => 'boolean',
        ]);
        $data['created_at'] = $data['updated_at'] = now();
        $id = DB::table('footer_links')->insertGetId($data);
        Cache::forget('site.footer_links');
        return response()->json(['success' => true, 'id' => $id]);
    }

    public function footerLinkUpdate(Request $request, $id) {
        $data = $request->only(['section','label','label_en','route_path','icon','sort_order','enabled']);
        $data['updated_at'] = now();
        DB::table('footer_links')->where('id', $id)->update($data);
        Cache::forget('site.footer_links');
        return response()->json(['success' => true]);
    }

    public function footerLinkDestroy($id) {
        DB::table('footer_links')->where('id', $id)->delete();
        Cache::forget('site.footer_links');
        return response()->json(['success' => true]);
    }

    // ─── Static Pages ───
    public function staticPages() {
        return response()->json([
            'success' => true,
            'data' => DB::table('static_pages')->orderBy('slug')->get(),
        ]);
    }

    public function staticPageShow($slug) {
        $page = DB::table('static_pages')->where('slug', $slug)->first();
        if (!$page) return response()->json(['success' => false, 'message' => 'Not found'], 404);
        return response()->json(['success' => true, 'data' => $page]);
    }

    public function staticPageUpdate(Request $request, $slug) {
        $data = $request->validate([
            'title'            => 'required|string|max:255',
            'content'          => 'required|string',
            'meta_description' => 'nullable|string',
            'meta_keywords'    => 'nullable|string|max:500',
            'published'        => 'boolean',
            'change_note'      => 'nullable|string',
        ]);

        $page = DB::table('static_pages')->where('slug', $slug)->first();
        if (!$page) return response()->json(['success' => false, 'message' => 'Not found'], 404);

        // 기존 content → 버전 이력에 저장
        DB::table('static_page_versions')->insert([
            'static_page_id' => $page->id,
            'version'        => $page->version,
            'content'        => $page->content,
            'changed_by'     => auth()->id(),
            'change_note'    => $data['change_note'] ?? null,
            'created_at'     => now(),
        ]);

        DB::table('static_pages')->where('id', $page->id)->update([
            'title'            => $data['title'],
            'content'          => $data['content'],
            'meta_description' => $data['meta_description'] ?? null,
            'meta_keywords'    => $data['meta_keywords'] ?? null,
            'published'        => $data['published'] ?? $page->published,
            'version'          => $page->version + 1,
            'updated_by'       => auth()->id(),
            'updated_at'       => now(),
        ]);

        // 호환: site_settings 에도 반영
        if (in_array($slug, ['about','terms','privacy'])) {
            DB::table('site_settings')->updateOrInsert(
                ['key' => $slug . '_page'],
                ['value' => $data['content'], 'group' => 'pages', 'updated_at' => now(), 'created_at' => now()]
            );
        }

        Cache::forget("site.static_page.{$slug}");
        Cache::forget('public_settings');

        try { event(new \App\Events\SiteSettingsUpdated([$slug . '_page'], 'pages')); } catch (\Throwable $e) {}

        return response()->json(['success' => true]);
    }

    public function staticPageVersions($slug) {
        $page = DB::table('static_pages')->where('slug', $slug)->first();
        if (!$page) return response()->json(['success' => false], 404);
        $versions = DB::table('static_page_versions')
            ->where('static_page_id', $page->id)
            ->orderByDesc('version')
            ->get();
        return response()->json(['success' => true, 'data' => $versions]);
    }

    // ─── FAQ ───
    public function faqs() {
        return response()->json([
            'success' => true,
            'data' => DB::table('faqs')->orderBy('category')->orderBy('sort_order')->get(),
        ]);
    }

    public function faqStore(Request $request) {
        $data = $request->validate([
            'category'   => 'required|string|max:100',
            'question'   => 'required|string|max:500',
            'answer'     => 'required|string',
            'sort_order' => 'integer',
            'published'  => 'boolean',
        ]);
        $data['created_at'] = $data['updated_at'] = now();
        $id = DB::table('faqs')->insertGetId($data);
        Cache::forget('site.faqs.all');
        return response()->json(['success' => true, 'id' => $id]);
    }

    public function faqUpdate(Request $request, $id) {
        $data = $request->only(['category','question','answer','sort_order','published']);
        $data['updated_at'] = now();
        DB::table('faqs')->where('id', $id)->update($data);
        Cache::forget('site.faqs.all');
        return response()->json(['success' => true]);
    }

    public function faqDestroy($id) {
        DB::table('faqs')->where('id', $id)->delete();
        Cache::forget('site.faqs.all');
        return response()->json(['success' => true]);
    }

    // ─── Settings History ───
    public function settingsHistory(Request $request) {
        $key = $request->query('key');
        $q = DB::table('site_setting_history')
            ->leftJoin('users', 'users.id', '=', 'site_setting_history.changed_by')
            ->select('site_setting_history.*', 'users.nickname as changed_by_name');
        if ($key) $q->where('setting_key', $key);
        return response()->json([
            'success' => true,
            'data' => $q->orderByDesc('site_setting_history.created_at')->limit(100)->get(),
        ]);
    }
}
