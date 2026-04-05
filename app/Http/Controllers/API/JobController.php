<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\JobPost;
use Illuminate\Http\Request;

class JobController extends Controller
{
    /**
     * GET /api/jobs
     */
    public function index(Request $request)
    {
        $query = JobPost::with('user:id,name,nickname,avatar')
            ->where('status', 'active');

        // Category filter
        if ($request->category) {
            $query->where('category', $request->category);
        }

        // Job type filter
        if ($request->type) {
            $query->where('job_type', $request->type);
        }

        // Region filter
        if ($request->region) {
            $query->where('region', 'like', '%' . $request->region . '%');
        }

        // Search
        if ($request->search) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                  ->orWhere('content', 'like', "%{$search}%")
                  ->orWhere('company_name', 'like', "%{$search}%");
            });
        }

        // Distance filter
        if ($request->lat && $request->lng) {
            $lat = (float) $request->lat;
            $lng = (float) $request->lng;
            $radius = (float) ($request->radius ?? 30);
            $query->selectRaw("job_posts.*, (3959 * acos(cos(radians(?)) * cos(radians(lat)) * cos(radians(lng) - radians(?)) + sin(radians(?)) * sin(radians(lat)))) AS distance", [$lat, $lng, $lat])
                  ->having('distance', '<=', $radius)
                  ->orderBy('distance');
        } else {
            $query->orderByDesc('is_pinned')->orderByDesc('created_at');
        }

        return response()->json([
            'success' => true,
            'data'    => $query->paginate(20),
        ]);
    }

    /**
     * GET /api/jobs/{id}
     */
    public function show($id)
    {
        $job = JobPost::with('user:id,name,nickname,avatar')->findOrFail($id);
        $job->increment('view_count');

        return response()->json([
            'success' => true,
            'data'    => $job,
        ]);
    }

    /**
     * POST /api/jobs
     */
    public function store(Request $request)
    {
        $request->validate([
            'title'         => 'required|string|max:200',
            'content'       => 'required|string',
            'company_name'  => 'nullable|string|max:200',
            'contact_email' => 'nullable|email',
            'contact_phone' => 'nullable|string|max:20',
            'job_type'      => 'nullable|string|max:50',
            'salary_range'  => 'nullable|string|max:100',
            'region'        => 'nullable|string|max:100',
            'address'       => 'nullable|string|max:255',
            'deadline'      => 'nullable|date',
        ]);

        $job = JobPost::create(array_merge(
            $request->only([
                'title', 'content', 'company_name', 'contact_email', 'contact_phone',
                'job_type', 'salary_range', 'region', 'address', 'deadline',
            ]),
            ['user_id' => auth()->id()]
        ));

        return response()->json([
            'success' => true,
            'message' => '채용공고가 등록되었습니다.',
            'data'    => $job,
        ], 201);
    }

    /**
     * PUT /api/jobs/{id}
     */
    public function update(Request $request, $id)
    {
        $job = JobPost::findOrFail($id);

        if ($job->user_id !== auth()->id() && !auth()->user()->is_admin) {
            return response()->json(['success' => false, 'message' => '수정 권한이 없습니다.'], 403);
        }

        $request->validate([
            'title'         => 'sometimes|string|max:200',
            'content'       => 'sometimes|string',
            'company_name'  => 'nullable|string|max:200',
            'contact_email' => 'nullable|email',
            'contact_phone' => 'nullable|string|max:20',
            'job_type'      => 'nullable|string|max:50',
            'salary_range'  => 'nullable|string|max:100',
            'region'        => 'nullable|string|max:100',
            'address'       => 'nullable|string|max:255',
            'deadline'      => 'nullable|date',
        ]);

        $job->update($request->only([
            'title', 'content', 'company_name', 'contact_email', 'contact_phone',
            'job_type', 'salary_range', 'region', 'address', 'deadline',
        ]));

        return response()->json([
            'success' => true,
            'message' => '수정되었습니다.',
            'data'    => $job->fresh(),
        ]);
    }

    /**
     * DELETE /api/jobs/{id}
     */
    public function destroy($id)
    {
        $job = JobPost::findOrFail($id);

        if ($job->user_id !== auth()->id() && !auth()->user()->is_admin) {
            return response()->json(['success' => false, 'message' => '삭제 권한이 없습니다.'], 403);
        }

        $job->delete();

        return response()->json([
            'success' => true,
            'message' => '삭제되었습니다.',
        ]);
    }
}
