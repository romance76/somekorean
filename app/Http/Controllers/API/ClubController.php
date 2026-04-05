<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Club;
use App\Models\ClubMember;
use App\Models\ClubPost;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Traits\HasDistanceFilter;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;

class ClubController extends Controller
{
    use HasDistanceFilter;
    public function index(Request $request)
    {
        $query = Club::with('creator:id,name,username,avatar');

        // 온라인/지역 필터
        if ($request->filter === 'online') {
            $query->where('is_online', true);
        } elseif ($request->filter === 'local') {
            $query->where('is_online', false);
            // 지역 동호회만 거리 필터 적용
            $this->applyDistanceFilter($query, $request, "latitude", "longitude");
        } else {
            // filter가 없으면 모두 표시, 지역 동호회에만 거리 필터 적용
            if ($request->lat && $request->lng && $request->radius) {
                $query->where(function ($q) use ($request) {
                    $q->where('is_online', true)
                      ->orWhere(function ($q2) use ($request) {
                          $q2->where('is_online', false);
                          $this->applyDistanceFilter($q2, $request, "latitude", "longitude");
                      });
                });
            }
        }

        if ($request->category) {
            $query->where('category', $request->category);
        }
        if ($request->search) {
            $query->where(function ($q) use ($request) {
                $q->where('name', 'like', '%' . $request->search . '%')
                  ->orWhere('description', 'like', '%' . $request->search . '%');
            });
        }
        if ($request->region) {
            $query->where('region', $request->region);
        }
        $clubs = $query->orderByDesc('created_at')->paginate(20);
        return response()->json($clubs);
    }

    public function show($id)
    {
        $club = Club::with([
            'creator:id,name,username,avatar',
            'members' => function ($q) {
                $q->where('status', 'approved')->with('user:id,name,username,avatar');
            },
        ])->findOrFail($id);

        $myMembership = null;
        if (Auth::check()) {
            $myMembership = ClubMember::where('club_id', $id)
                ->where('user_id', Auth::id())
                ->first();
        }

        return response()->json([
            'club' => $club,
            'my_membership' => $myMembership,
        ]);
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name'        => 'required|string|max:100',
            'category'    => 'required|string|max:50',
            'description' => 'nullable|string|max:2000',
            'region'      => 'nullable|string|max:100',
            'cover_image' => 'nullable|image|max:3072',
            'is_approval' => 'nullable',
            'is_online'   => 'nullable',
            'zip_code'    => 'nullable|string|max:10',
            'address'     => 'nullable|string|max:255',
            'latitude'    => 'nullable|numeric',
            'longitude'   => 'nullable|numeric',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $coverPath = null;
        if ($request->hasFile('cover_image')) {
            $coverPath = $request->file('cover_image')->store('clubs', 'public');
        }

        $isOnline = filter_var($request->is_online, FILTER_VALIDATE_BOOLEAN);
        $latitude = $request->latitude;
        $longitude = $request->longitude;
        $region = $request->region;

        // 지역 동호회이고 zip_code가 있으면 위/경도 변환
        if (!$isOnline && $request->zip_code) {
            $coords = $this->geocodeZipCode($request->zip_code);
            if ($coords) {
                $latitude = $coords['lat'];
                $longitude = $coords['lng'];
                if (!$region && isset($coords['city'])) {
                    $region = $coords['city'] . ($coords['state'] ? ', ' . $coords['state'] : '');
                }
            }
        }

        // 상세 주소가 있고 zip_code가 없으면 주소로 geocoding
        if (!$isOnline && $request->address && !$request->zip_code) {
            $coords = $this->geocodeAddress($request->address);
            if ($coords) {
                $latitude = $coords['lat'];
                $longitude = $coords['lng'];
            }
        }

        $club = Club::create([
            'creator_id'  => Auth::id(),
            'name'        => $request->name,
            'category'    => $request->category,
            'description' => $request->description,
            'region'      => $region,
            'cover_image' => $coverPath,
            'is_approval' => filter_var($request->is_approval, FILTER_VALIDATE_BOOLEAN),
            'member_count' => 1,
            'is_online'   => $isOnline,
            'zip_code'    => $request->zip_code,
            'address'     => $request->address,
            'latitude'    => $latitude,
            'longitude'   => $longitude,
        ]);

        ClubMember::create([
            'club_id' => $club->id,
            'user_id' => Auth::id(),
            'role'    => 'owner',
            'status'  => 'approved',
        ]);

        return response()->json([
            'message' => '동호회가 생성되었습니다.',
            'club'    => $club->load('creator'),
        ], 201);
    }

    public function update(Request $request, $id)
    {
        $club = Club::findOrFail($id);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 수정할 수 있습니다.'], 403);
        }

        $validator = Validator::make($request->all(), [
            'name'        => 'sometimes|string|max:100',
            'description' => 'nullable|string|max:2000',
            'region'      => 'nullable|string|max:100',
            'cover_image' => 'nullable|image|max:3072',
            'is_approval' => 'nullable',
            'is_online'   => 'nullable',
            'zip_code'    => 'nullable|string|max:10',
            'address'     => 'nullable|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        if ($request->hasFile('cover_image')) {
            if ($club->cover_image) {
                Storage::disk('public')->delete($club->cover_image);
            }
            $club->cover_image = $request->file('cover_image')->store('clubs', 'public');
        }

        $club->fill($request->only(['name', 'description', 'region']));
        if ($request->has('is_approval')) {
            $club->is_approval = filter_var($request->is_approval, FILTER_VALIDATE_BOOLEAN);
        }
        if ($request->has('is_online')) {
            $club->is_online = filter_var($request->is_online, FILTER_VALIDATE_BOOLEAN);
        }
        if ($request->has('zip_code')) {
            $club->zip_code = $request->zip_code;
        }
        if ($request->has('address')) {
            $club->address = $request->address;
        }

        // 지역 동호회이고 zip_code가 변경되었으면 재 geocoding
        if (!$club->is_online && $request->zip_code) {
            $coords = $this->geocodeZipCode($request->zip_code);
            if ($coords) {
                $club->latitude = $coords['lat'];
                $club->longitude = $coords['lng'];
                if (isset($coords['city'])) {
                    $club->region = $coords['city'] . ($coords['state'] ? ', ' . $coords['state'] : '');
                }
            }
        }

        // 주소로 geocoding
        if (!$club->is_online && $request->address && !$request->zip_code) {
            $coords = $this->geocodeAddress($request->address);
            if ($coords) {
                $club->latitude = $coords['lat'];
                $club->longitude = $coords['lng'];
            }
        }

        // 온라인 동호회로 변경 시 위치 정보 초기화
        if ($club->is_online) {
            $club->latitude = null;
            $club->longitude = null;
            $club->zip_code = null;
            $club->address = null;
        }

        $club->save();

        return response()->json(['message' => '수정되었습니다.', 'club' => $club]);
    }

    public function destroy($id)
    {
        $club = Club::findOrFail($id);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 삭제할 수 있습니다.'], 403);
        }

        ClubMember::where('club_id', $id)->delete();
        ClubPost::where('club_id', $id)->delete();

        if ($club->cover_image) {
            Storage::disk('public')->delete($club->cover_image);
        }

        $club->delete();

        return response()->json(['message' => '동호회가 삭제되었습니다.']);
    }

    public function join($id)
    {
        $club = Club::findOrFail($id);

        $existing = ClubMember::where('club_id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if ($existing) {
            if ($existing->status === 'pending') {
                return response()->json(['message' => '이미 가입 신청 중입니다.'], 400);
            }
            return response()->json(['message' => '이미 가입된 동호회입니다.'], 400);
        }

        $status = $club->is_approval ? 'pending' : 'approved';

        ClubMember::create([
            'club_id' => $id,
            'user_id' => Auth::id(),
            'role'    => 'member',
            'status'  => $status,
        ]);

        if (!$club->is_approval) {
            $club->increment('member_count');
        }

        $message = $club->is_approval
            ? '가입 신청이 완료되었습니다. 방장의 승인을 기다려주세요.'
            : '동호회에 가입되었습니다.';

        return response()->json(['message' => $message, 'status' => $status]);
    }

    public function leave($id)
    {
        $member = ClubMember::where('club_id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$member) {
            return response()->json(['message' => '가입되지 않은 동호회입니다.'], 400);
        }

        if ($member->role === 'owner') {
            return response()->json(['message' => '방장은 탈퇴할 수 없습니다. 방장을 양도하거나 동호회를 삭제해주세요.'], 400);
        }

        $member->delete();

        $club = Club::find($id);
        if ($club && $club->member_count > 0) {
            $club->decrement('member_count');
        }

        return response()->json(['message' => '동호회에서 탈퇴했습니다.']);
    }

    public function myClubs()
    {
        $clubIds = ClubMember::where('user_id', Auth::id())
            ->where('status', 'approved')
            ->pluck('club_id');

        $clubs = Club::with('creator:id,name,username,avatar')
            ->whereIn('id', $clubIds)
            ->orderByDesc('created_at')
            ->get();

        return response()->json($clubs);
    }

    public function posts($id)
    {
        $club = Club::findOrFail($id);
        $posts = ClubPost::where('club_id', $id)
            ->with('user:id,name,username,avatar')
            ->latest()
            ->paginate(20);
        return response()->json($posts);
    }

    public function createPost(Request $request, $id)
    {
        $club = Club::findOrFail($id);

        $member = ClubMember::where('club_id', $id)
            ->where('user_id', Auth::id())
            ->where('status', 'approved')
            ->first();

        if (!$member) {
            return response()->json(['message' => '동호회 회원만 게시글을 작성할 수 있습니다.'], 403);
        }

        $request->validate([
            'title'   => 'required|string|max:200',
            'content' => 'required|string|max:10000',
        ]);

        $post = ClubPost::create([
            'club_id' => $id,
            'user_id' => Auth::id(),
            'title'   => $request->title,
            'content' => $request->content,
        ]);

        return response()->json([
            'message' => '게시글이 등록되었습니다.',
            'post' => $post->load('user:id,name,username,avatar'),
        ], 201);
    }

    // ===== 방장 기능 =====

    public function getMembers($id)
    {
        $club = Club::findOrFail($id);

        $members = DB::table('club_members')
            ->join('users', 'users.id', '=', 'club_members.user_id')
            ->where('club_members.club_id', $id)
            ->where('club_members.status', 'approved')
            ->select(
                'users.id',
                'users.name',
                'users.username',
                'users.avatar',
                'club_members.role',
                'club_members.status',
                'club_members.created_at as joined_at'
            )
            ->orderByRaw("FIELD(club_members.role, 'owner', 'member')")
            ->orderBy('club_members.created_at')
            ->get();

        return response()->json($members);
    }

    public function getPendingMembers($id)
    {
        $club = Club::findOrFail($id);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 가입 신청 목록을 볼 수 있습니다.'], 403);
        }

        $pending = DB::table('club_members')
            ->join('users', 'users.id', '=', 'club_members.user_id')
            ->where('club_members.club_id', $id)
            ->where('club_members.status', 'pending')
            ->select(
                'users.id',
                'users.name',
                'users.username',
                'users.avatar',
                'club_members.created_at as applied_at'
            )
            ->orderBy('club_members.created_at')
            ->get();

        return response()->json($pending);
    }

    public function approveMember($clubId, $userId)
    {
        $club = Club::findOrFail($clubId);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 승인할 수 있습니다.'], 403);
        }

        $updated = DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->where('status', 'pending')
            ->update(['status' => 'approved', 'updated_at' => now()]);

        if (!$updated) {
            return response()->json(['message' => '해당 신청을 찾을 수 없습니다.'], 404);
        }

        $club->increment('member_count');

        return response()->json(['message' => '승인되었습니다.']);
    }

    public function rejectMember($clubId, $userId)
    {
        $club = Club::findOrFail($clubId);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 거절할 수 있습니다.'], 403);
        }

        $deleted = DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->where('status', 'pending')
            ->delete();

        if (!$deleted) {
            return response()->json(['message' => '해당 신청을 찾을 수 없습니다.'], 404);
        }

        return response()->json(['message' => '거절되었습니다.']);
    }

    public function kickMember($clubId, $userId)
    {
        $club = Club::findOrFail($clubId);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 회원을 강퇴할 수 있습니다.'], 403);
        }

        $target = DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->first();

        if (!$target) {
            return response()->json(['message' => '해당 회원을 찾을 수 없습니다.'], 404);
        }

        if ($target->role === 'owner') {
            return response()->json(['message' => '방장은 강퇴할 수 없습니다.'], 400);
        }

        DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->delete();

        if ($target->status === 'approved') {
            $club->decrement('member_count');
        }

        return response()->json(['message' => '강퇴되었습니다.']);
    }

    public function changeRole($clubId, $userId)
    {
        $club = Club::findOrFail($clubId);

        if ($club->creator_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 역할을 변경할 수 있습니다.'], 403);
        }

        $role = request('role');
        if (!in_array($role, ['member', 'admin'])) {
            return response()->json(['message' => '유효하지 않은 역할입니다.'], 422);
        }

        $updated = DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->where('status', 'approved')
            ->where('role', '!=', 'owner')
            ->update(['role' => $role, 'updated_at' => now()]);

        if (!$updated) {
            return response()->json(['message' => '해당 회원을 찾을 수 없습니다.'], 404);
        }

        return response()->json(['message' => '역할이 변경되었습니다.']);
    }

    public function transferOwner($clubId, $userId)
    {
        $club = Club::findOrFail($clubId);

        if ($club->creator_id !== Auth::id()) {
            return response()->json(['message' => '방장만 양도할 수 있습니다.'], 403);
        }

        $target = DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->where('status', 'approved')
            ->first();

        if (!$target) {
            return response()->json(['message' => '해당 회원을 찾을 수 없습니다.'], 404);
        }

        DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', Auth::id())
            ->update(['role' => 'member', 'updated_at' => now()]);

        DB::table('club_members')
            ->where('club_id', $clubId)
            ->where('user_id', $userId)
            ->update(['role' => 'owner', 'updated_at' => now()]);

        $club->update(['creator_id' => $userId]);

        return response()->json(['message' => '방장이 양도되었습니다.']);
    }

    // ===== 집코드/주소 Geocoding =====

    /**
     * 집코드 → 위/경도 변환 API (프론트엔드에서 호출)
     */
    public function geocodeZip(Request $request)
    {
        $request->validate(['zip_code' => 'required|string|max:10']);
        $result = $this->geocodeZipCode($request->zip_code);
        if ($result) {
            return response()->json($result);
        }
        return response()->json(['message' => '유효하지 않은 집코드입니다.'], 422);
    }

    /**
     * 집코드 → 위/경도 변환 (Zippopotam.us 무료 API)
     */
    private function geocodeZipCode($zipCode)
    {
        try {
            $response = Http::timeout(5)->get("https://api.zippopotam.us/us/{$zipCode}");
            if ($response->successful()) {
                $data = $response->json();
                return [
                    'lat' => (float)$data['places'][0]['latitude'],
                    'lng' => (float)$data['places'][0]['longitude'],
                    'city' => $data['places'][0]['place name'] ?? null,
                    'state' => $data['places'][0]['state abbreviation'] ?? null,
                ];
            }
        } catch (\Exception $e) {
            \Log::warning('Zip code geocoding failed: ' . $e->getMessage());
        }
        return null;
    }

    /**
     * 주소 → 위/경도 변환 (Google Geocoding API)
     */
    private function geocodeAddress($address)
    {
        $key = config('services.google.maps_key', env('GOOGLE_MAPS_KEY'));
        if (!$key) return null;

        try {
            $response = Http::timeout(5)->get('https://maps.googleapis.com/maps/api/geocode/json', [
                'address' => $address,
                'key' => $key,
            ]);
            if ($response->successful()) {
                $results = $response->json('results');
                if (!empty($results)) {
                    $location = $results[0]['geometry']['location'];
                    return ['lat' => $location['lat'], 'lng' => $location['lng']];
                }
            }
        } catch (\Exception $e) {
            \Log::warning('Address geocoding failed: ' . $e->getMessage());
        }
        return null;
    }
}
