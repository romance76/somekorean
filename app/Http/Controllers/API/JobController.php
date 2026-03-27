<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\JobPost;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class JobController extends Controller
{
    public function index(Request $request)
    {
        $query = JobPost::with('user:id,name,username')
            ->where('status', 'active')
            ->orderByDesc('is_pinned')
            ->orderByDesc('created_at');

        if ($request->region) $query->where('region', 'like', '%'.$request->region.'%');
        if ($request->type)   $query->where('job_type', $request->type);
        if ($request->search) {
            $query->where(function($q) use ($request) {
                $q->where('title', 'like', '%'.$request->search.'%')
                  ->orWhere('company_name', 'like', '%'.$request->search.'%');
            });
        }

        return response()->json($query->paginate(20));
    }

    public function store(Request $request)
    {
        $request->validate([
            'title'   => 'required|string|max:200',
            'content' => 'required|string',
        ]);
        $job = JobPost::create(array_merge($request->only(['title','content','company_name','contact_email','contact_phone','region','address','job_type','salary_range','deadline']), ['user_id' => Auth::id()]));
        return response()->json(['message' => '채용공고가 등록되었습니다.', 'job' => $job], 201);
    }

    public function show(JobPost $job)
    {
        $job->increment('view_count');
        return response()->json($job->load('user:id,name,username'));
    }

    public function destroy(JobPost $job)
    {
        if ($job->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        $job->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }
}
