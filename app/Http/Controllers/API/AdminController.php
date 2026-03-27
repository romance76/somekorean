<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Post;
use App\Models\JobPost;
use App\Models\MarketItem;
use App\Models\Business;
use App\Models\Report;
use Illuminate\Http\Request;

class AdminController extends Controller
{
    public function stats()
    {
        return response()->json([
            'users'       => User::count(),
            'posts'       => Post::where('status','active')->count(),
            'jobs'        => JobPost::where('status','active')->count(),
            'market'      => MarketItem::where('status','active')->count(),
            'businesses'  => Business::where('status','active')->count(),
            'reports'     => Report::where('status','pending')->count(),
            'new_users_today' => User::whereDate('created_at', today())->count(),
            'new_posts_today' => Post::whereDate('created_at', today())->count(),
        ]);
    }

    public function users(Request $request)
    {
        $query = User::query();
        if ($request->search) {
            $query->where(function($q) use ($request) {
                $q->where('name', 'like', '%'.$request->search.'%')
                  ->orWhere('email', 'like', '%'.$request->search.'%')
                  ->orWhere('username', 'like', '%'.$request->search.'%');
            });
        }
        if ($request->status) $query->where('status', $request->status);
        return response()->json($query->orderByDesc('created_at')->paginate(20));
    }

    public function banUser(Request $request, User $user)
    {
        if ($user->is_admin) return response()->json(['message' => '관리자는 정지할 수 없습니다.'], 400);
        $user->update(['status' => 'banned']);
        return response()->json(['message' => "{$user->name} 계정이 정지되었습니다."]);
    }

    public function unbanUser(User $user)
    {
        $user->update(['status' => 'active']);
        return response()->json(['message' => "{$user->name} 계정 정지가 해제되었습니다."]);
    }

    public function reports(Request $request)
    {
        $reports = Report::with(['reporter:id,name,username', 'reportable'])
            ->where('status', $request->status ?? 'pending')
            ->orderByDesc('created_at')
            ->paginate(20);
        return response()->json($reports);
    }

    public function dismissReport(Report $report)
    {
        $report->update(['status' => 'dismissed', 'reviewed_by' => auth()->id()]);
        return response()->json(['message' => '신고가 처리되었습니다.']);
    }
}
