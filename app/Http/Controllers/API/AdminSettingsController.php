<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AdminSettingsController extends Controller
{
    // =========================================================================
    // 공개 설정 (인증 불필요)
    // =========================================================================

    /**
     * GET /api/settings/public
     * 공개 사이트 설정 반환
     */
    public function getPublicSettings()
    {
        try {
            $row   = DB::table('site_settings')->where('key', 'menu_settings')->first();
            $menus = $row ? json_decode($row->value, true) : [];

            return response()->json([
                'success'   => true,
                'menus'     => is_array($menus) ? $menus : [],
                'site_name' => DB::table('site_settings')->where('key', 'site_name')->value('value') ?: 'SomeKorean',
                'logo_url'  => DB::table('site_settings')->where('key', 'logo_url')->value('value'),
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success'   => true,
                'menus'     => [],
                'site_name' => 'SomeKorean',
                'logo_url'  => null,
            ]);
        }
    }

    /**
     * GET /api/site-settings/logo
     * 현재 로고 URL 반환
     */
    public function getLogo()
    {
        $url = DB::table('site_settings')->where('key', 'logo_url')->value('value');
        return response()->json(['success' => true, 'logo_url' => $url ?: '/images/logo.jpg']);
    }

    // =========================================================================
    // 관리자 설정 (인증 필요)
    // =========================================================================

    /**
     * GET /api/admin/settings
     * 모든 사이트 설정을 그룹별로 반환
     */
    public function index()
    {
        try {
            $allSettings = DB::table('site_settings')->get();

            // 그룹 분류
            $grouped = [
                'company'       => [],
                'site'          => [],
                'seo'           => [],
                'payment'       => [],
                'notification'  => [],
                'footer'        => [],
                'terms'         => [],
                'menus'         => [],
                'elder'         => [],
                'other'         => [],
            ];

            $groupPrefixes = [
                'site_name' => 'company', 'site_subtitle' => 'company', 'company_name' => 'company',
                'ceo_name' => 'company', 'business_number' => 'company', 'address' => 'company',
                'phone' => 'company', 'email' => 'company', 'founded_at' => 'company',
                'logo_url' => 'company', 'favicon_url' => 'company',
                'meta_' => 'seo', 'seo_' => 'seo', 'google_analytics' => 'seo',
                'stripe_' => 'payment', 'payment_' => 'payment', 'pg_' => 'payment',
                'vapid_' => 'notification', 'notification_' => 'notification',
                'footer_' => 'footer',
                'terms_' => 'terms',
                'menu_' => 'menus',
                'elder_' => 'elder',
                'allow_' => 'site', 'email_verification' => 'site', 'auto_approve' => 'site',
                'min_password' => 'site', 'points_' => 'site', 'checkin_points' => 'site',
                'signup_points' => 'site', 'post_points' => 'site', 'comment_points' => 'site',
                'max_upload' => 'site', 'allowed_extensions' => 'site', 'maintenance_' => 'site',
                'kakao_' => 'site',
            ];

            foreach ($allSettings as $setting) {
                $assignedGroup = 'other';
                foreach ($groupPrefixes as $prefix => $group) {
                    if (str_starts_with($setting->key, $prefix)) {
                        $assignedGroup = $group;
                        break;
                    }
                }
                $grouped[$assignedGroup][$setting->key] = $setting->value;
            }

            return response()->json(['success' => true, 'data' => $grouped]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * PUT /api/admin/settings
     * 설정 업데이트 (key/value 쌍)
     */
    public function update(Request $request)
    {
        try {
            $validated = $request->validate([
                'settings' => 'required|array',
            ]);

            foreach ($validated['settings'] as $key => $value) {
                // 값이 배열/객체이면 JSON으로 인코딩
                $storedValue = is_array($value) || is_object($value)
                    ? json_encode($value)
                    : (is_bool($value) ? ($value ? '1' : '0') : (string) $value);

                DB::table('site_settings')->updateOrInsert(
                    ['key' => $key],
                    ['value' => $storedValue, 'updated_at' => now()]
                );
            }

            return response()->json(['success' => true, 'message' => '설정이 저장되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * POST /api/admin/settings/logo
     * 로고 업로드
     */
    public function uploadLogo(Request $request)
    {
        try {
            $request->validate([
                'logo' => 'required|image|mimes:jpg,jpeg,png,gif,webp|max:5120',
            ]);

            $file = $request->file('logo');

            // images 디렉토리 확인
            $imagesDir = public_path('images');
            if (!is_dir($imagesDir)) {
                mkdir($imagesDir, 0755, true);
            }

            $file->move($imagesDir, 'logo_00.jpg');

            $url = '/images/logo_00.jpg?v=' . time();
            DB::table('site_settings')->updateOrInsert(
                ['key' => 'logo_url'],
                ['value' => $url, 'updated_at' => now()]
            );

            return response()->json([
                'success'  => true,
                'message'  => '로고가 업로드되었습니다.',
                'logo_url' => $url,
            ]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    // =========================================================================
    // 개별 설정 섹션 저장 (기존 호환)
    // =========================================================================

    /**
     * POST /api/admin/settings/company
     */
    public function saveCompany(Request $request)
    {
        $fields = [
            'site_name', 'site_subtitle', 'company_name', 'ceo_name', 'business_number',
            'address', 'phone', 'email', 'founded_at', 'logo_url', 'favicon_url',
            'meta_description', 'meta_keywords',
        ];

        return $this->saveFields($request, $fields, '회사 정보가 저장되었습니다.');
    }

    /**
     * POST /api/admin/settings/site
     */
    public function saveSite(Request $request)
    {
        $fields = [
            'allow_registration', 'email_verification', 'auto_approve', 'min_password_length',
            'allow_withdrawal', 'points_enabled', 'checkin_points', 'signup_points',
            'post_points', 'comment_points', 'max_upload_mb', 'allowed_extensions',
            'maintenance_mode', 'maintenance_reason', 'maintenance_until',
            'google_analytics_id', 'kakao_api_key',
        ];

        return $this->saveFields($request, $fields, '사이트 설정이 저장되었습니다.');
    }

    /**
     * POST /api/admin/settings/footer
     */
    public function saveFooter(Request $request)
    {
        DB::table('site_settings')->updateOrInsert(
            ['key' => 'footer_data'],
            ['value' => json_encode($request->all()), 'updated_at' => now()]
        );
        return response()->json(['success' => true, 'message' => '푸터가 저장되었습니다.']);
    }

    /**
     * POST /api/admin/settings/terms/{type}
     */
    public function saveTerms(Request $request, $type)
    {
        $request->validate(['content' => 'required|string']);

        DB::table('site_settings')->updateOrInsert(
            ['key' => "terms_{$type}"],
            ['value' => $request->content, 'updated_at' => now()]
        );

        return response()->json(['success' => true, 'message' => '약관이 저장되었습니다.']);
    }

    /**
     * POST /api/admin/settings/notifications
     */
    public function saveNotifications(Request $request)
    {
        DB::table('site_settings')->updateOrInsert(
            ['key' => 'notification_settings'],
            ['value' => json_encode($request->all()), 'updated_at' => now()]
        );
        return response()->json(['success' => true, 'message' => '알림 설정이 저장되었습니다.']);
    }

    // =========================================================================
    // 메뉴 관리
    // =========================================================================

    /**
     * GET /api/admin/settings/menus
     */
    public function getMenus()
    {
        $saved = DB::table('site_settings')->where('key', 'menu_settings')->first();
        $menus = $saved ? json_decode($saved->value, true) : [];
        return response()->json(['success' => true, 'data' => is_array($menus) ? $menus : []]);
    }

    /**
     * POST /api/admin/settings/menus/batch
     */
    public function saveMenusBatch(Request $request)
    {
        $request->validate(['menus' => 'required|array']);

        DB::table('site_settings')->updateOrInsert(
            ['key' => 'menu_settings'],
            ['value' => json_encode($request->menus), 'updated_at' => now()]
        );

        return response()->json(['success' => true, 'message' => '메뉴 설정이 저장되었습니다.']);
    }

    // =========================================================================
    // 결제 설정
    // =========================================================================

    /**
     * POST /api/admin/settings/stripe
     */
    public function saveStripeKeys(Request $request)
    {
        $fields = [
            'stripe_publishable_key' => $request->input('stripe_publishable_key'),
            'stripe_secret_key'      => $request->input('stripe_secret_key'),
            'stripe_webhook_secret'  => $request->input('stripe_webhook_secret'),
            'stripe_test_mode'       => $request->input('stripe_test_mode', true) ? '1' : '0',
        ];

        foreach ($fields as $key => $val) {
            if ($val !== null) {
                DB::table('site_settings')->updateOrInsert(
                    ['key' => $key],
                    ['value' => $val, 'updated_at' => now()]
                );
            }
        }

        return response()->json(['success' => true, 'message' => 'Stripe 설정이 저장되었습니다.']);
    }

    // =========================================================================
    // 헬퍼
    // =========================================================================

    /**
     * 필드 목록을 site_settings 테이블에 저장
     */
    private function saveFields(Request $request, array $fields, string $message)
    {
        foreach ($fields as $field) {
            if ($request->has($field)) {
                $val = $request->input($field);
                $storedValue = is_bool($val) ? ($val ? '1' : '0') : (string) $val;

                DB::table('site_settings')->updateOrInsert(
                    ['key' => $field],
                    ['value' => $storedValue, 'updated_at' => now()]
                );
            }
        }

        return response()->json(['success' => true, 'message' => $message]);
    }
}
