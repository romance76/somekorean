<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Report;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class ReportController extends Controller
{
    // 신고 제출
    public function store(Request $request)
    {
        $request->validate([
            'reportable_type' => 'required|string',  // post, comment, market_item, job, user 등
            'reportable_id'   => 'required|integer',
            'reason'          => 'required|in:spam,illegal,obscene,advertisement,scam,inappropriate,hate,false_info,other',
            'description'     => 'nullable|string|max:500',
        ]);

        $typeMap = [
            'post'        => \App\Models\Post::class,
            'comment'     => \App\Models\Comment::class,
            'job'         => \App\Models\JobPost::class,
            'job_post'    => \App\Models\JobPost::class,
            'market_item' => \App\Models\MarketItem::class,
            'business'    => \App\Models\Business::class,
            'user'        => \App\Models\User::class,
        ];

        $reportableType = $typeMap[$request->reportable_type] ?? $request->reportable_type;

        // 중복 신고 방지
        $existing = Report::where('reporter_id', Auth::id())
            ->where('reportable_type', $reportableType)
            ->where('reportable_id', $request->reportable_id)
            ->exists();

        if ($existing) {
            return response()->json(['error' => '이미 신고했습니다'], 400);
        }

        Report::create([
            'reporter_id'     => Auth::id(),
            'reportable_type' => $reportableType,
            'reportable_id'   => $request->reportable_id,
            'reason'          => $request->reason,
            'detail'          => $request->description,
            'ip_address'      => $request->ip(),
        ]);

        // 신고 횟수 체크
        $reportCount = Report::where('reportable_type', $reportableType)
            ->where('reportable_id', $request->reportable_id)
            ->count();

        // 3회 이상 -> 자동 숨김
        if ($reportCount >= 3) {
            $this->hideContent($reportableType, $request->reportable_id);
        }

        // 5회 이상 -> 관리자 알림
        if ($reportCount >= 5) {
            $this->notifyAdmins($request->reportable_type, $request->reportable_id, $reportCount);
        }

        return response()->json([
            'success'      => true,
            'message'      => '신고가 접수되었습니다. 검토 후 처리하겠습니다.',
            'report_count' => $reportCount,
        ], 201);
    }

    private function hideContent(string $modelClass, int $id): void
    {
        $tableMap = [
            \App\Models\Post::class       => 'posts',
            \App\Models\Comment::class    => 'comments',
            \App\Models\MarketItem::class => 'market_items',
            \App\Models\JobPost::class    => 'jobs',
        ];

        $table = $tableMap[$modelClass] ?? null;
        if ($table) {
            try {
                DB::table($table)->where('id', $id)->update(['status' => 'hidden']);
            } catch (\Exception $e) {
                // 테이블에 status 컬럼 없으면 무시
            }
        }
    }

    private function notifyAdmins(string $type, int $id, int $count): void
    {
        try {
            $admins = DB::table('users')->where('is_admin', true)->pluck('id');
            foreach ($admins as $adminId) {
                DB::table('notifications')->insert([
                    'user_id'    => $adminId,
                    'type'       => 'report_alert',
                    'title'      => '신고 누적 콘텐츠',
                    'body'       => "{$type} #{$id}에 신고가 {$count}회 누적되었습니다.",
                    'url'        => '/admin/security',
                    'is_read'    => false,
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);
            }
        } catch (\Exception $e) {
            // notifications 테이블 구조 문제 시 무시
        }
    }
}
