<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Mentor;
use App\Models\MentorRequest;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class MentorController extends Controller
{
    // 멘토 목록
    public function index(Request $request)
    {
        $q = Mentor::with('user:id,name,username,avatar')
            ->where('is_available', true);

        if ($request->field && $request->field !== 'all') {
            $q->where('field', $request->field);
        }
        if ($request->search) {
            $q->where(function ($sq) use ($request) {
                $sq->where('bio', 'like', "%{$request->search}%")
                   ->orWhereHas('user', fn($u) => $u->where('name', 'like', "%{$request->search}%"));
            });
        }

        return response()->json($q->latest()->paginate(20));
    }

    // 내 멘토 프로필
    public function myProfile()
    {
        $mentor = Mentor::with('user:id,name,username,avatar')
            ->where('user_id', Auth::id())->first();
        return response()->json($mentor);
    }

    // 멘토 등록 / 수정
    public function saveProfile(Request $request)
    {
        $request->validate([
            'field'            => 'required|string|max:50',
            'bio'              => 'required|string|max:1000',
            'years_experience' => 'required|integer|min:0|max:50',
            'company'          => 'nullable|string|max:100',
            'position'         => 'nullable|string|max:100',
            'skills'           => 'nullable|array',
        ]);

        $mentor = Mentor::updateOrCreate(
            ['user_id' => Auth::id()],
            [
                'field'            => $request->field,
                'bio'              => $request->bio,
                'years_experience' => $request->years_experience,
                'company'          => $request->company,
                'position'         => $request->position,
                'skills'           => $request->skills ?? [],
                'is_available'     => true,
            ]
        );

        return response()->json($mentor->load('user:id,name,username,avatar'));
    }

    // 멘토링 신청
    public function request(Request $request, $mentorId)
    {
        $request->validate(['message' => 'required|string|max:500']);

        $mentor = Mentor::findOrFail($mentorId);

        if ($mentor->user_id === Auth::id()) {
            return response()->json(['message' => '자신에게 신청할 수 없습니다.'], 422);
        }

        $exists = MentorRequest::where('mentor_id', $mentorId)
            ->where('mentee_id', Auth::id())
            ->whereIn('status', ['pending', 'accepted'])
            ->exists();

        if ($exists) {
            return response()->json(['message' => '이미 신청하셨습니다.'], 422);
        }

        $req = MentorRequest::create([
            'mentor_id' => $mentorId,
            'mentee_id' => Auth::id(),
            'message'   => $request->message,
            'status'    => 'pending',
        ]);

        return response()->json($req, 201);
    }

    // 받은 신청 목록 (멘토 측)
    public function myRequests()
    {
        $mentor = Mentor::where('user_id', Auth::id())->firstOrFail();
        $reqs = MentorRequest::with('mentee:id,name,username,avatar')
            ->where('mentor_id', $mentor->id)
            ->latest()->get();
        return response()->json($reqs);
    }

    // 신청 수락/거절
    public function respond(Request $request, $requestId)
    {
        $request->validate(['status' => 'required|in:accepted,rejected']);
        $mentor = Mentor::where('user_id', Auth::id())->firstOrFail();
        $req = MentorRequest::where('mentor_id', $mentor->id)->findOrFail($requestId);
        $req->update(['status' => $request->status]);
        return response()->json($req);
    }

    // 가용 여부 토글
    public function toggleAvailable()
    {
        $mentor = Mentor::where('user_id', Auth::id())->firstOrFail();
        $mentor->update(['is_available' => !$mentor->is_available]);
        return response()->json(['is_available' => $mentor->is_available]);
    }
}
