<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AdminSettingsController extends Controller
{
    // GET /api/settings/public (공개 — 인증 불필요)
    public function getPublicSettings() {
        $row   = DB::table('site_settings')->where('key', 'menu_settings')->first();
        $menus = $row ? json_decode($row->value, true) : [];

        return response()->json([
            'menus'     => is_array($menus) ? $menus : [],
            'site_name' => DB::table('site_settings')->where('key', 'site_name')->value('value') ?: 'SomeKorean',
            'logo_url'  => DB::table('site_settings')->where('key', 'logo_url')->value('value'),
        ]);
    }

    // GET /api/admin/settings/all
    public function getAll() {
        $settings = DB::table('site_settings')->pluck('value', 'key');
        return response()->json($settings);
    }

    // POST /api/admin/settings/company
    public function saveCompany(Request $r) {
        $fields = ['site_name','site_subtitle','company_name','ceo_name','business_number','address','phone','email','founded_at','logo_url','favicon_url','meta_description','meta_keywords'];
        foreach ($fields as $f) {
            if ($r->has($f)) {
                DB::table('site_settings')->updateOrInsert(['key'=>$f], ['value'=>$r->$f, 'updated_at'=>now()]);
            }
        }
        return response()->json(['message'=>'회사 정보가 저장되었습니다.']);
    }

    // POST /api/admin/settings/site
    public function saveSite(Request $r) {
        $fields = ['allow_registration','email_verification','auto_approve','min_password_length','allow_withdrawal','points_enabled','checkin_points','signup_points','post_points','comment_points','max_upload_mb','allowed_extensions','maintenance_mode','maintenance_reason','maintenance_until','google_analytics_id','kakao_api_key'];
        foreach ($fields as $f) {
            if ($r->has($f)) {
                DB::table('site_settings')->updateOrInsert(['key'=>$f], ['value'=>is_bool($r->$f) ? ($r->$f ? '1' : '0') : $r->$f, 'updated_at'=>now()]);
            }
        }
        return response()->json(['message'=>'사이트 설정이 저장되었습니다.']);
    }

    // POST /api/admin/settings/footer
    public function saveFooter(Request $r) {
        DB::table('site_settings')->updateOrInsert(['key'=>'footer_data'], ['value'=>json_encode($r->all()), 'updated_at'=>now()]);
        return response()->json(['message'=>'푸터가 저장되었습니다.']);
    }

    // POST /api/admin/settings/terms/{type}
    public function saveTerms(Request $r, $type) {
        DB::table('site_settings')->updateOrInsert(['key'=>"terms_{$type}"], ['value'=>$r->content, 'updated_at'=>now()]);
        return response()->json(['message'=>'약관이 저장되었습니다.']);
    }

    // POST /api/admin/settings/payment-gateway
    public function savePaymentGateway(Request $r) {
        $fields = ['stripe_publishable_key','stripe_secret_key','stripe_webhook_secret','stripe_enabled','stripe_test_mode','payment_currency','min_payment_amount'];
        foreach ($fields as $f) {
            if ($r->has($f)) {
                DB::table('site_settings')->updateOrInsert(['key'=>$f], ['value'=>$r->$f, 'updated_at'=>now()]);
            }
        }
        return response()->json(['message'=>'결제 설정이 저장되었습니다.']);
    }

    // POST /api/admin/settings/notifications
    public function saveNotifications(Request $r) {
        DB::table('site_settings')->updateOrInsert(['key'=>'notification_settings'], ['value'=>json_encode($r->all()), 'updated_at'=>now()]);
        return response()->json(['message'=>'알림 설정이 저장되었습니다.']);
    }

    // GET /api/admin/settings/menus
    public function getMenus() {
        $saved = DB::table('site_settings')->where('key','menu_settings')->first();
        if ($saved) return response()->json(json_decode($saved->value, true));
        return response()->json([]);
    }

    // POST /api/admin/settings/menus/batch
    public function saveMenusBatch(Request $r) {
        DB::table('site_settings')->updateOrInsert(['key'=>'menu_settings'], ['value'=>json_encode($r->menus), 'updated_at'=>now()]);
        return response()->json(['message'=>'메뉴 설정이 저장되었습니다.']);
    }

    // POST /api/admin/settings/boards/{key}
    public function saveBoard(Request $r, $key) {
        DB::table('site_settings')->updateOrInsert(['key'=>"board_{$key}"], ['value'=>json_encode($r->all()), 'updated_at'=>now()]);
        return response()->json(['message'=>'게시판 설정이 저장되었습니다.']);
    }

    // GET /api/admin/payments
    public function getPayments(Request $r) {
        try {
            $q = DB::table('payments')
                ->leftJoin('users','payments.user_id','=','users.id')
                ->select('payments.*','users.name as user_name','users.email as user_email')
                ->orderByDesc('payments.created_at');
            if ($r->status) $q->where('payments.status',$r->status);
            if ($r->type)   $q->where('payments.type',$r->type);
            if ($r->from)   $q->whereDate('payments.created_at','>=',$r->from);
            if ($r->to)     $q->whereDate('payments.created_at','<=',$r->to);
            return response()->json($q->paginate(20));
        } catch (\Exception $e) {
            return response()->json(['data'=>[],'total'=>0]);
        }
    }

    // POST /api/admin/payments/{id}/refund
    public function refundPayment($id) {
        try {
            DB::table('payments')->where('id',$id)->update(['status'=>'refunded','updated_at'=>now()]);
            return response()->json(['message'=>'환불 처리되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['message'=>'처리 실패.'],500);
        }
    }

    // GET /api/admin/banners
    public function getBanners() {
        try {
            return response()->json(DB::table('banners')->orderBy('order')->get());
        } catch (\Exception $e) { return response()->json([]); }
    }

    // POST /api/admin/banners
    public function createBanner(Request $r) {
        try {
            DB::table('banners')->insert([
                'name'=>$r->name,'position'=>$r->position,'image_url'=>$r->image_url,
                'link_url'=>$r->link_url,'new_tab'=>$r->new_tab??false,
                'start_at'=>$r->start_at,'end_at'=>$r->end_at,'order'=>$r->order??0,
                'active'=>$r->active??true,'advertiser'=>$r->advertiser,
                'amount'=>$r->amount??0,'memo'=>$r->memo,'created_at'=>now(),'updated_at'=>now(),
            ]);
            return response()->json(['message'=>'배너가 등록되었습니다.']);
        } catch (\Exception $e) { return response()->json(['message'=>'실패.'],500); }
    }

    // PUT /api/admin/banners/{id}
    public function updateBanner(Request $r, $id) {
        try {
            DB::table('banners')->where('id',$id)->update(array_merge($r->all(),['updated_at'=>now()]));
            return response()->json(['message'=>'배너가 수정되었습니다.']);
        } catch (\Exception $e) { return response()->json(['message'=>'실패.'],500); }
    }

    // DELETE /api/admin/banners/{id}
    public function deleteBanner($id) {
        try { DB::table('banners')->where('id',$id)->delete(); } catch (\Exception $e) {}
        return response()->json(['message'=>'배너가 삭제되었습니다.']);
    }

    // POST /api/admin/users/{id}/adjust-points
    public function adjustPoints(Request $r, $id) {
        try {
            $user = \App\Models\User::findOrFail($id);
            $amount = (int)$r->amount;
            $user->increment('points_total', $amount);
            DB::table('point_logs')->insert([
                'user_id'=>$id,'type'=>$amount>0?'earn':'spend',
                'action'=>'admin_adjust','amount'=>abs($amount),
                'balance_after'=>max(0,$user->points_total),'memo'=>$r->reason,'created_at'=>now(),'updated_at'=>now(),
            ]);
            return response()->json(['message'=>'포인트가 조정되었습니다.','new_points'=>$user->points_total]);
        } catch (\Exception $e) { return response()->json(['message'=>'실패.'],500); }
    }

    // POST /api/admin/users/bulk-action
    public function bulkAction(Request $r) {
        $ids = $r->ids ?? [];
        $action = $r->action;
        try {
            if ($action === 'ban')    \App\Models\User::whereIn('id',$ids)->update(['status'=>'banned']);
            if ($action === 'active') \App\Models\User::whereIn('id',$ids)->update(['status'=>'active']);
            return response()->json(['message'=>count($ids).'명에게 처리 완료.']);
        } catch (\Exception $e) { return response()->json(['message'=>'실패.'],500); }
    }
}
