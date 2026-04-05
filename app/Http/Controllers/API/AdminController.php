<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Post;
use App\Models\JobPost;
use App\Models\MarketItem;
use App\Models\Business;
use App\Models\Report;
use App\Models\ChatRoom;
use App\Models\ChatMessage;
use App\Models\Club;
use App\Models\Event;
use App\Models\ElderSetting;
use App\Models\Checkin;
use App\Models\Ride;
use App\Models\GroupBuy;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

// Additional models (loaded via try/catch if tables may not exist)
// App\Models\Short, App\Models\DriverProfile

class AdminController extends Controller
{
    // ─── 개요 통계 ────────────────────────────────────────────
    public function stats()
    {
        $elderCount = $groupBuys = $mentors = $rides = 0;
        try { $elderCount = ElderSetting::where('elder_mode', true)->count(); } catch (\Exception $e) {}
        try { $groupBuys  = DB::table('group_buys')->where('status', 'open')->count(); } catch (\Exception $e) {}
        try { $mentors    = DB::table('mentors')->where('is_available', true)->count(); } catch (\Exception $e) {}
        try { $rides      = DB::table('rides')->count(); } catch (\Exception $e) {}

        return response()->json([
            'users'           => User::count(),
            'posts'           => Post::where('status', 'active')->count(),
            'jobs'            => JobPost::where('status', 'active')->count(),
            'market'          => MarketItem::where('status', 'active')->count(),
            'businesses'      => Business::where('status', 'active')->count(),
            'reports'         => Report::where('status', 'pending')->count(),
            'chat_rooms'      => ChatRoom::count(),
            'clubs'           => Club::count(),
            'events'          => Event::count(),
            'group_buys'      => $groupBuys,
            'mentors'         => $mentors,
            'rides'           => $rides,
            'elder_users'     => $elderCount,
            'banned_users'    => User::where('status', 'banned')->count(),
            'new_users_today' => User::whereDate('created_at', today())->count(),
            'new_posts_today' => Post::whereDate('created_at', today())->count(),
        ]);
    }

    public function activity()
    {
        $days = collect(range(6, 0))->map(function ($i) {
            $date = now()->subDays($i)->toDateString();
            return [
                'date'  => now()->subDays($i)->format('m/d'),
                'users' => User::whereDate('created_at', $date)->count(),
                'posts' => Post::whereDate('created_at', $date)->count(),
            ];
        });
        return response()->json($days);
    }

    // ─── 회원 관리 ────────────────────────────────────────────
    public function users(Request $request)
    {
        $query = User::query();
        if ($request->search) {
            $query->where(function ($q) use ($request) {
                $q->where('name',     'like', '%'.$request->search.'%')
                  ->orWhere('email',    'like', '%'.$request->search.'%')
                  ->orWhere('username', 'like', '%'.$request->search.'%');
            });
        }
        if ($request->status) $query->where('status', $request->status);
        if ($request->role === 'admin') $query->where('is_admin', true);
        return response()->json($query->orderByDesc('created_at')->paginate(25));
    }

    public function userDetail($id)
    {
        $user = User::findOrFail($id);

        // Count stats
        $user->posts_count = $user->posts()->count();
        $user->comments_count = $user->comments()->count();
        $user->reports_count = Report::where('reporter_id', $id)->count();

        // Recent posts (last 10)
        $user->recent_posts = $user->posts()
            ->select('id', 'title', 'board_id', 'created_at')
            ->latest()->take(10)->get();

        // Recent comments (last 10)
        $user->recent_comments = $user->comments()
            ->select('id', 'content', 'post_id', 'created_at')
            ->with('post:id,title')
            ->latest()->take(10)->get();

        // Payment history
        $user->payments = DB::table('payments')
            ->where('user_id', $id)
            ->orderBy('created_at', 'desc')
            ->take(20)->get();

        // Point logs
        try {
            $user->point_logs = $user->pointLogs()
                ->select('id', 'action', 'amount', 'description', 'created_at')
                ->latest()->take(20)->get();
        } catch (\Exception $e) {
            $user->point_logs = [];
        }

        // Businesses owned
        $user->businesses = Business::where('user_id', $id)->get();

        return response()->json($user);
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

    public function deleteUser(User $user)
    {
        if ($user->is_admin) return response()->json(['message' => '관리자는 삭제할 수 없습니다.'], 400);
        $user->delete();
        return response()->json(['message' => '회원이 삭제되었습니다.']);
    }

    // ─── 콘텐츠/신고 관리 ─────────────────────────────────────
    public function reports(Request $request)
    {
        $reports = Report::with(['reporter:id,name,username', 'reportable'])
            ->where('status', $request->status ?? 'pending')
            ->orderByDesc('created_at')
            ->paginate(25);
        return response()->json($reports);
    }

    public function dismissReport(Report $report)
    {
        $report->update(['status' => 'dismissed', 'reviewed_by' => auth()->id()]);
        return response()->json(['message' => '신고가 처리되었습니다.']);
    }

    public function posts(Request $request)
    {
        $q = Post::with('user:id,name,username')->latest();
        if ($request->search) $q->where('title', 'like', '%'.$request->search.'%');
        return response()->json($q->paginate(25));
    }

    public function deletePost($id)
    {
        Post::findOrFail($id)->delete();
        return response()->json(['message' => '게시글이 삭제되었습니다.']);
    }

    public function jobs(Request $request)
    {
        $q = JobPost::with('user:id,name')->latest();
        if ($request->search) $q->where('title', 'like', '%'.$request->search.'%');
        return response()->json($q->paginate(25));
    }

    public function deleteJob($id)
    {
        JobPost::findOrFail($id)->delete();
        return response()->json(['message' => '구인구직이 삭제되었습니다.']);
    }

    public function market(Request $request)
    {
        $q = MarketItem::with('user:id,name')->latest();
        if ($request->search) $q->where('title', 'like', '%'.$request->search.'%');
        return response()->json($q->paginate(25));
    }

    public function deleteMarket($id)
    {
        MarketItem::findOrFail($id)->delete();
        return response()->json(['message' => '중고장터 글이 삭제되었습니다.']);
    }

    // ─── 업소록 관리 ─────────────────────────────────────────
    public function businesses(Request $request)
    {
        $q = Business::with('user:id,name')->latest();
        if ($request->search) $q->where('name', 'like', '%'.$request->search.'%');
        if ($request->status) $q->where('status', $request->status);
        return response()->json($q->paginate(25));
    }

    public function approveBusiness($id)
    {
        Business::findOrFail($id)->update(['status' => 'active', 'verified' => true]);
        return response()->json(['message' => '업소가 승인되었습니다.']);
    }

    public function updateBusiness(Request $req, $id)
    {
        $business = Business::findOrFail($id);
        $business->update($req->only(['name','english_name','category','owner_name','phone','email','website','address','description','hours','status']));
        return response()->json($business);
    }

    public function rejectBusiness(Request $req, $id)
    {
        $business = Business::findOrFail($id);
        $business->update(['status' => 'rejected', 'rejection_reason' => $req->reason]);
        return response()->json(['message' => 'Rejected']);
    }

    public function deleteBusiness($id)
    {
        Business::findOrFail($id)->delete();
        return response()->json(['message' => '업소가 삭제되었습니다.']);
    }

    // ─── 라이드 관리 ─────────────────────────────────────────
    public function rides(Request $request)
    {
        try {
            $q = DB::table('rides')
                ->leftJoin('users as p', 'rides.passenger_id', '=', 'p.id')
                ->leftJoin('users as d', 'rides.driver_id',    '=', 'd.id')
                ->select('rides.*', 'p.name as passenger_name', 'd.name as driver_name')
                ->orderByDesc('rides.created_at');
            if ($request->status) $q->where('rides.status', $request->status);
            return response()->json($q->paginate(25));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }

    public function approveRide($id)
    {
        $ride = Ride::findOrFail($id);
        $ride->update(['status' => 'accepted']);
        return response()->json(['message' => 'Approved']);
    }

    public function rejectRide($id)
    {
        $ride = Ride::findOrFail($id);
        $ride->update(['status' => 'cancelled']);
        return response()->json(['message' => 'Rejected']);
    }

    public function completeRide($id)
    {
        $ride = Ride::findOrFail($id);
        $ride->update(['status' => 'completed', 'completed_at' => now()]);
        return response()->json(['message' => 'Completed']);
    }

    public function ridePayouts()
    {
        $payouts = DB::table('rides')
            ->select('driver_id', DB::raw('COUNT(*) as completed_rides'), DB::raw('SUM(fare) as total_fare'))
            ->where('status', 'completed')
            ->groupBy('driver_id')
            ->get()
            ->map(function($p) {
                $driver = User::find($p->driver_id);
                $p->driver_name = $driver->name ?? 'Unknown';
                $p->commission = $p->total_fare * 0.20;
                $p->payout_amount = $p->total_fare * 0.80;
                return $p;
            });
        return response()->json($payouts);
    }

    public function payoutDriver(Request $req, $driverId)
    {
        // Mark payout as processed (placeholder logic)
        return response()->json(['message' => "Driver {$driverId} payout processed."]);
    }

    // ─── 공동구매 관리 ───────────────────────────────────────
    public function groupbuys(Request $request)
    {
        try {
            $q = DB::table('group_buys')
                ->leftJoin('users', 'group_buys.user_id', '=', 'users.id')
                ->select('group_buys.*', 'users.name as user_name')
                ->orderByDesc('group_buys.created_at');
            if ($request->status) $q->where('group_buys.status', $request->status);
            return response()->json($q->paginate(25));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }

    public function createGroupBuy(Request $req)
    {
        $gb = GroupBuy::create([
            'user_id' => auth()->id(),
            'title' => $req->title,
            'description' => $req->description,
            'price' => $req->price,
            'min_participants' => $req->min_participants,
            'max_participants' => $req->max_participants,
            'deadline' => $req->deadline,
            'category' => $req->category ?? '기타',
            'status' => 'open',
        ]);
        return response()->json($gb, 201);
    }

    public function approveGroupBuy($id)
    {
        $gb = GroupBuy::findOrFail($id);
        $gb->update(['status' => 'open']);
        return response()->json(['message' => 'Approved']);
    }

    public function updateGroupBuy(Request $req, $id)
    {
        $gb = GroupBuy::findOrFail($id);
        $gb->update($req->only(['title','description','price','min_participants','max_participants','deadline','category','status']));
        return response()->json($gb);
    }

    public function deleteGroupBuy($id)
    {
        try { DB::table('group_buys')->where('id', $id)->delete(); } catch (\Exception $e) {}
        return response()->json(['message' => '공동구매가 삭제되었습니다.']);
    }

    // ─── 멘토링 관리 ─────────────────────────────────────────
    public function mentors(Request $request)
    {
        try {
            $q = DB::table('mentors')
                ->leftJoin('users', 'mentors.user_id', '=', 'users.id')
                ->select('mentors.*', 'users.name as user_name', 'users.email as user_email')
                ->orderByDesc('mentors.created_at');
            return response()->json($q->paginate(25));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }

    public function toggleMentor($id)
    {
        try {
            $mentor = DB::table('mentors')->where('id', $id)->first();
            $newVal = !$mentor->is_available;
            DB::table('mentors')->where('id', $id)->update(['is_available' => $newVal]);
            return response()->json(['message' => '멘토 상태 변경.', 'is_available' => $newVal]);
        } catch (\Exception $e) {
            return response()->json(['message' => '처리 실패.'], 500);
        }
    }

    // ─── 채팅방 관리 ─────────────────────────────────────────
    public function chatRooms(Request $request)
    {
        $q = ChatRoom::withCount('messages')->latest();
        if ($request->search) $q->where('name', 'like', '%'.$request->search.'%');
        return response()->json($q->paginate(25));
    }

    public function chatMessages($roomId)
    {
        $messages = ChatMessage::with('user:id,name,username')
            ->where('chat_room_id', $roomId)
            ->latest()->limit(50)->get();
        return response()->json($messages);
    }

    public function createChatRoom(Request $req)
    {
        $room = ChatRoom::create([
            'name' => $req->name,
            'description' => $req->description,
            'type' => $req->type ?? 'public',
            'max_members' => $req->max_members ?? 100,
            'created_by' => auth()->id(),
        ]);
        return response()->json($room, 201);
    }

    public function updateChatRoom(Request $req, $id)
    {
        $room = ChatRoom::findOrFail($id);
        $room->update($req->only(['name','description','type','max_members']));
        return response()->json($room);
    }

    public function deleteChatRoom($id)
    {
        ChatRoom::findOrFail($id)->delete();
        return response()->json(['message' => '채팅방이 삭제되었습니다.']);
    }

    public function deleteChatMessage($id)
    {
        ChatMessage::findOrFail($id)->delete();
        return response()->json(['message' => '메시지가 삭제되었습니다.']);
    }

    // ─── 노인 안심 모니터링 ──────────────────────────────────
    public function elderMonitor()
    {
        try {
            $elders = ElderSetting::with('user:id,name,username,email')
                ->where('elder_mode', true)->get()
                ->map(function ($s) {
                    $overdue = true;
                    if ($s->last_checkin_at) {
                        $overdue = $s->last_checkin_at->diffInHours(now()) > $s->checkin_interval;
                    }
                    return [
                        'id'               => $s->id,
                        'user'             => $s->user,
                        'guardian_name'    => $s->guardian_name,
                        'guardian_phone'   => $s->guardian_phone
                            ? substr($s->guardian_phone, 0, 3).'****'.substr($s->guardian_phone, -4) : null,
                        'checkin_interval' => $s->checkin_interval,
                        'last_checkin_at'  => $s->last_checkin_at,
                        'last_sos_at'      => $s->last_sos_at,
                        'is_overdue'       => $overdue,
                        'alert_sent'       => $s->alert_sent,
                    ];
                });
            return response()->json($elders);
        } catch (\Exception $e) {
            return response()->json([]);
        }
    }

    public function elderDetail($id)
    {
        $elder = ElderSetting::with('user')->findOrFail($id);
        $elder->checkins = Checkin::where('user_id', $elder->user_id)->latest()->take(30)->get();
        return response()->json($elder);
    }

    public function resetCheckin($id)
    {
        $elder = ElderSetting::findOrFail($id);
        $elder->update(['last_checkin_at' => now(), 'is_overdue' => false]);
        return response()->json(['message' => 'Reset']);
    }

    public function sendElderAlert($id)
    {
        $elder = ElderSetting::with('user')->findOrFail($id);
        // Placeholder: send alert to guardian
        $elder->update(['alert_sent' => true]);
        return response()->json(['message' => 'Alert sent to guardian for ' . ($elder->user->name ?? 'Unknown')]);
    }

    public function saveElderSettings(Request $req)
    {
        $settings = $req->only(['default_interval','alert_delay','sos_recipients','emergency_contacts']);
        foreach ($settings as $key => $value) {
            DB::table('site_settings')->updateOrInsert(
                ['key' => "elder_$key"],
                ['value' => is_array($value) ? json_encode($value) : $value, 'updated_at' => now()]
            );
        }
        return response()->json(['message' => 'Saved']);
    }

    // ─── 동호회 관리 ─────────────────────────────────────────
    public function getClubs(Request $req)
    {
        $clubs = Club::with('creator:id,name')
            ->when($req->search, fn($q) => $q->where('name', 'like', "%{$req->search}%"))
            ->latest()->paginate(15);
        return response()->json($clubs);
    }

    public function deleteClub($id)
    {
        Club::destroy($id);
        return response()->json(['message' => 'Deleted']);
    }

    // ─── 이벤트 관리 ─────────────────────────────────────────
    public function getEvents(Request $req)
    {
        $events = Event::with('user:id,name')
            ->when($req->search, fn($q) => $q->where('title', 'like', "%{$req->search}%"))
            ->latest()->paginate(15);
        return response()->json($events);
    }

    public function createEvent(Request $req)
    {
        $event = Event::create([
            'title'       => $req->title,
            'description' => $req->description ?? '',
            'location'    => $req->location ?? '',
            'event_date'  => $req->event_date ?? $req->date ?? now(),
            'category'    => $req->category ?? '기타',
            'image_url'   => $req->image_url ?? null,
            'user_id'     => $req->user()->id ?? 1,
            'max_attendees' => $req->max_attendees ?? null,
        ]);
        return response()->json($event, 201);
    }

    public function updateEvent(Request $req, $id)
    {
        $event = Event::findOrFail($id);
        $event->update($req->only(['title', 'description', 'location', 'event_date', 'date', 'category', 'image_url', 'max_attendees']));
        return response()->json($event);
    }

    public function deleteEvent($id)
    {
        Event::destroy($id);
        return response()->json(['message' => 'Deleted']);
    }

    // ─── 숏츠 관리 ───────────────────────────────────────────
    public function blindShort($id) {
        $short = DB::table('shorts')->where('id', $id)->first();
        if (!$short) return response()->json(['error' => 'Not found'], 404);
        $newActive = $short->is_active ? 0 : 1;
        DB::table('shorts')->where('id', $id)->update(['is_active' => $newActive, 'updated_at' => now()]);
        return response()->json(['is_active' => $newActive, 'message' => $newActive ? '활성화됨' : '숨김 처리됨']);
    }

    public function getShorts(Request $req)
    {
        try {
            $q = DB::table('shorts')
                ->leftJoin('users', 'shorts.user_id', '=', 'users.id')
                ->select('shorts.*', 'users.name as user_name')
                ->orderByDesc('shorts.created_at');
            if ($req->search) {
                $q->where('shorts.title', 'like', "%{$req->search}%");
            }
            if ($req->platform) {
                $q->where('shorts.platform', $req->platform);
            }
            if ($req->status === 'active') {
                $q->where('shorts.is_active', 1);
            } elseif ($req->status === 'hidden') {
                $q->where('shorts.is_active', 0);
            }
            return response()->json($q->paginate(15));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }

    public function deleteShort($id)
    {
        try {
            DB::table('shorts')->where('id', $id)->delete();
        } catch (\Exception $e) {}
        return response()->json(['message' => 'Deleted']);
    }


    // ─── 드라이버 관리 ───────────────────────────────────────
    public function getDrivers(Request $req)
    {
        try {
            $q = DB::table('driver_profiles')
                ->leftJoin('users', 'driver_profiles.user_id', '=', 'users.id')
                ->select(
                    'driver_profiles.*',
                    'users.name as name',
                    'users.email as email',
                    'users.phone as phone'
                )
                ->orderByDesc('driver_profiles.created_at');
            if ($req->status) {
                $q->where('driver_profiles.status', $req->status);
            }
            return response()->json($q->paginate(15));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }

    public function approveDriver($id)
    {
        try {
            DB::table('driver_profiles')->where('id', $id)->update(['status' => 'active', 'updated_at' => now()]);
        } catch (\Exception $e) {}
        return response()->json(['message' => 'Approved']);
    }

    public function rejectDriver($id)
    {
        try {
            DB::table('driver_profiles')->where('id', $id)->update(['status' => 'rejected', 'updated_at' => now()]);
        } catch (\Exception $e) {}
        return response()->json(['message' => 'Rejected']);
    }

    // ─── 회사/업체 관리 (businesses 별칭) ──────────────────────
    public function getCompanies(Request $req)
    {
        $q = Business::with('user:id,name')->latest();
        if ($req->search) $q->where('name', 'like', '%'.$req->search.'%');
        if ($req->status) $q->where('status', $req->status);
        return response()->json($q->paginate(15));
    }

    public function approveCompany($id)
    {
        Business::findOrFail($id)->update(['status' => 'active', 'verified' => true]);
        return response()->json(['message' => 'Approved']);
    }

    public function rejectCompany(Request $req, $id)
    {
        $business = Business::findOrFail($id);
        $business->update(['status' => 'rejected', 'rejection_reason' => $req->reason]);
        return response()->json(['message' => 'Rejected']);
    }

    // ─── 어드민 채팅 관리 (신규) ──────────────────────────────

    // Get all chat rooms with stats for admin
    public function adminChatRooms()
    {
        $rooms = \App\Models\ChatRoom::withCount('messages')
            ->orderBy('created_at', 'desc')
            ->get()
            ->map(function($room) {
                $last = $room->messages()->latest()->first();
                return array_merge($room->toArray(), [
                    'messages_count' => $room->messages_count,
                    'last_message' => $last?->message ? mb_substr($last->message, 0, 50) : null,
                    'last_message_at' => $last?->created_at,
                ]);
            });

        $totalMessages = \App\Models\ChatMessage::count();
        $todayMessages = \App\Models\ChatMessage::whereDate('created_at', today())->count();

        return response()->json([
            'rooms' => $rooms,
            'stats' => [
                'total_rooms' => $rooms->count(),
                'active_rooms' => $rooms->where('is_open', true)->count(),
                'total_messages' => $totalMessages,
                'today_messages' => $todayMessages,
            ]
        ]);
    }

    // Get messages for a specific room (admin view - all messages)
    public function adminChatMessages($id)
    {
        $room = \App\Models\ChatRoom::findOrFail($id);
        $messages = \App\Models\ChatMessage::where('chat_room_id', $id)
            ->with('user:id,name,username,avatar')
            ->orderBy('created_at', 'desc')
            ->limit(100)
            ->get()
            ->reverse()
            ->values();

        return response()->json([
            'room' => $room,
            'messages' => $messages,
        ]);
    }

    // Toggle room open/close
    public function adminToggleChatRoom($id)
    {
        $room = \App\Models\ChatRoom::findOrFail($id);
        $room->is_open = !$room->is_open;
        $room->save();
        return response()->json(['success' => true, 'is_open' => $room->is_open]);
    }

    // Delete a chat room
    public function adminDeleteChatRoom($id)
    {
        $room = \App\Models\ChatRoom::findOrFail($id);
        $room->messages()->delete();
        $room->delete();
        return response()->json(['success' => true]);
    }

    // Delete a single message
    public function adminDeleteChatMessage($id)
    {
        \App\Models\ChatMessage::findOrFail($id)->delete();
        return response()->json(['success' => true]);
    }

    // Create a new chat room
    public function adminCreateChatRoom(\Illuminate\Http\Request $request)
    {
        $data = $request->validate([
            'name' => 'required|string|max:100',
            'description' => 'nullable|string|max:500',
            'type' => 'required|in:public,regional,theme,announcement',
            'icon' => 'nullable|string|max:10',
        ]);

        $slug = \Illuminate\Support\Str::slug($data['name']) . '-' . time();

        $room = \App\Models\ChatRoom::create([
            'name' => $data['name'],
            'slug' => $slug,
            'description' => $data['description'] ?? '',
            'type' => $data['type'],
            'icon' => $data['icon'] ?? '💬',
            'is_open' => true,
        ]);

        return response()->json(['success' => true, 'room' => $room]);
    }

    // ─── 채팅 킥 ────────────────────────────────────────────
    public function kickFromChat($roomId, $userId)
    {
        try {
            DB::table('chat_room_members')
                ->where('room_id', $roomId)
                ->where('user_id', $userId)
                ->delete();
        } catch (\Exception $e) {}
        return response()->json(['message' => 'Kicked']);
    }

    // ─── 신고 해결 ──────────────────────────────────────────
    public function resolveReport(Request $req, $id)
    {
        $report = Report::findOrFail($id);
        $report->update([
            'status'          => 'resolved',
            'resolved_action' => $req->action,
            'resolved_at'     => now(),
            'reviewed_by'     => auth()->id(),
        ]);
        return response()->json(['message' => 'Resolved']);
    }

    // ─── 쇼핑 딜 관리 ───────────────────────────────────────
    public function adminShoppingDeals(\Illuminate\Http\Request $request)
    {
        if (!\Illuminate\Support\Facades\Schema::hasTable('shopping_deals')) {
            return response()->json([]);
        }
        $deals = DB::table('shopping_deals')
            ->orderBy('published_at', 'desc')
            ->limit(100)
            ->get();
        return response()->json($deals);
    }

    public function adminToggleShoppingDeal($id)
    {
        if (!\Illuminate\Support\Facades\Schema::hasTable('shopping_deals')) {
            return response()->json(['success' => false]);
        }
        $deal = DB::table('shopping_deals')->find($id);
        if (!$deal) return response()->json(['success' => false], 404);
        DB::table('shopping_deals')->where('id', $id)->update([
            'is_active'  => !$deal->is_active,
            'updated_at' => now(),
        ]);
        return response()->json(['success' => true]);
    }

    public function adminDeleteShoppingDeal($id)
    {
        if (!\Illuminate\Support\Facades\Schema::hasTable('shopping_deals')) {
            return response()->json(['success' => false]);
        }
        DB::table('shopping_deals')->where('id', $id)->delete();
        return response()->json(['success' => true]);
    }

    // ── 뉴스 관리 ──────────────────────────────────────────────────────
    public function newsStats() {
        $total = \DB::table('news')->count();
        $today = \DB::table('news')->whereDate('published_at', today())->count();
        $sources = \DB::table('news')->distinct()->pluck('source')->count();
        $totalLikes = \DB::table('content_likes')->where('likeable_type', 'App\Models\News')->count();
        return response()->json([
            'totalNews' => $total,
            'todayNews' => $today,
            'feedCount' => $sources,
            'totalLikes' => $totalLikes,
        ]);
    }

    public function newsList(Request $request) {
        $q = \DB::table('news');
        if ($request->search) {
            $q->where('title', 'like', '%'.$request->search.'%');
        }
        if ($request->category) {
            $q->where('category', $request->category);
        }
        if ($request->source) {
            $q->where('source', $request->source);
        }
        $q->orderByDesc('published_at');
        return response()->json($q->paginate(20));
    }

    public function deleteNews($id) {
        \DB::table('news')->where('id', $id)->delete();
        return response()->json(['ok' => true]);
    }

    // ── 매칭 관리 ──────────────────────────────────────────────────────
    public function matchingStats() {
        return response()->json([
            'totalProfiles' => \DB::table('match_profiles')->count(),
            'totalLikes'    => \DB::table('match_likes')->count(),
            'verified'      => \DB::table('match_profiles')->where('verified', 1)->count(),
            'visible'       => \DB::table('match_profiles')->where('visibility', 'public')->count(),
        ]);
    }

    public function matchingProfiles(Request $request) {
        $q = \DB::table('match_profiles as mp')
            ->leftJoin('users as u', 'mp.user_id', '=', 'u.id')
            ->select('mp.*', 'u.username', 'u.email');
        if ($request->search) {
            $q->where('mp.nickname', 'like', '%'.$request->search.'%');
        }
        $q->orderByDesc('mp.created_at');
        return response()->json($q->paginate(20));
    }

    public function deleteMatchProfile($id) {
        \DB::table('match_profiles')->where('id', $id)->delete();
        \DB::table('match_likes')->where('from_user_id', $id)->orWhere('to_user_id', $id)->delete();
        return response()->json(['ok' => true]);
    }

    // ── 친구 관리 ──────────────────────────────────────────────────────
    public function friendsStats() {
        return response()->json([
            'total'   => \DB::table('friends')->count(),
            'today'   => \DB::table('friends')->whereDate('created_at', today())->count(),
            'blocked' => \DB::table('user_blocks')->count(),
        ]);
    }


    public function mentorRequests() {
        return response()->json(
            \DB::table('mentor_requests as mr')
                ->leftJoin('users as u', 'mr.mentee_id', '=', 'u.id')
                ->leftJoin('mentors as m', 'mr.mentor_id', '=', 'm.id')
                ->select('mr.*', 'u.username as mentee_name', 'm.nickname as mentor_name')
                ->orderByDesc('mr.created_at')
                ->paginate(20)
        );
    }

    public function approveMentorRequest($id) {
        \DB::table('mentor_requests')->where('id', $id)->update(['status' => 'accepted', 'responded_at' => now()]);
        return response()->json(['ok' => true]);
    }

    public function rejectMentorRequest($id) {
        \DB::table('mentor_requests')->where('id', $id)->update(['status' => 'rejected', 'responded_at' => now()]);
        return response()->json(['ok' => true]);
    }

    public function saveMentorSettings(Request $request) {
        return response()->json(['ok' => true]);
    }

    // ─── 보안: IP 차단 관리 ──────────────────────────────────────

    public function ipBans(Request $request)
    {
        try {
            $q = DB::table('ip_bans')->orderByDesc('created_at');

            if ($request->search) {
                $q->where('ip_address', 'like', '%'.$request->search.'%')
                  ->orWhere('reason', 'like', '%'.$request->search.'%');
            }

            if ($request->type === 'auto') {
                $q->where('reason', 'like', '%자동%');
            } elseif ($request->type === 'manual') {
                $q->where('reason', 'not like', '%자동%');
            }

            if ($request->status === 'active') {
                $q->where(function ($qq) {
                    $qq->whereNull('expires_at')
                       ->orWhere('expires_at', '>', now());
                });
            } elseif ($request->status === 'expired') {
                $q->where('expires_at', '<=', now());
            }

            $bans = $q->paginate(25);

            // 통계
            $stats = [
                'total'        => DB::table('ip_bans')->count(),
                'active'       => DB::table('ip_bans')->where(function ($q) {
                    $q->whereNull('expires_at')->orWhere('expires_at', '>', now());
                })->count(),
                'auto_blocked' => DB::table('ip_bans')->where('reason', 'like', '%자동%')->count(),
                'permanent'    => DB::table('ip_bans')->whereNull('expires_at')->count(),
            ];

            return response()->json(['bans' => $bans, 'stats' => $stats]);
        } catch (\Exception $e) {
            return response()->json([
                'bans'  => ['data' => [], 'total' => 0],
                'stats' => ['total' => 0, 'active' => 0, 'auto_blocked' => 0, 'permanent' => 0],
            ]);
        }
    }

    public function addIpBan(Request $request)
    {
        $request->validate([
            'ip_address' => 'required|string',
            'reason'     => 'required|string|max:500',
            'duration'   => 'required|in:1h,1d,7d,30d,permanent',
        ]);

        $expiresAt = match ($request->duration) {
            '1h'        => now()->addHour(),
            '1d'        => now()->addDay(),
            '7d'        => now()->addDays(7),
            '30d'       => now()->addDays(30),
            'permanent' => null,
        };

        try {
            DB::table('ip_bans')->insert([
                'ip_address' => $request->ip_address,
                'reason'     => $request->reason,
                'banned_by'  => auth()->id(),
                'expires_at' => $expiresAt,
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'IP 차단 추가 실패'], 500);
        }

        return response()->json(['message' => 'IP가 차단되었습니다.']);
    }

    public function removeIpBan($id)
    {
        try {
            DB::table('ip_bans')->where('id', $id)->delete();
        } catch (\Exception $e) {
            return response()->json(['error' => '삭제 실패'], 500);
        }
        return response()->json(['message' => 'IP 차단이 해제되었습니다.']);
    }

    // ─── 보안: 신고 관리 (강화) ──────────────────────────────────

    public function securityReports(Request $request)
    {
        try {
            $q = DB::table('reports')
                ->leftJoin('users', 'reports.reporter_id', '=', 'users.id')
                ->select(
                    'reports.*',
                    'users.name as reporter_name',
                    'users.username as reporter_username'
                );

            if ($request->status) {
                $q->where('reports.status', $request->status);
            }

            if ($request->type) {
                $q->where('reports.reportable_type', 'like', '%'.$request->type.'%');
            }

            $reports = $q->orderByDesc('reports.created_at')->paginate(25);

            // 통계
            $stats = [
                'total'   => DB::table('reports')->count(),
                'pending' => DB::table('reports')->where('status', 'pending')->count(),
                'today'   => DB::table('reports')->whereDate('created_at', today())->count(),
            ];

            return response()->json(['reports' => $reports, 'stats' => $stats]);
        } catch (\Exception $e) {
            return response()->json([
                'reports' => ['data' => [], 'total' => 0],
                'stats'   => ['total' => 0, 'pending' => 0, 'today' => 0],
            ]);
        }
    }

    public function processReport(Request $request, $id)
    {
        $request->validate([
            'action' => 'required|in:dismiss,hide,delete,ban_user',
        ]);

        try {
            $report = DB::table('reports')->where('id', $id)->first();
            if (!$report) {
                return response()->json(['error' => '신고를 찾을 수 없습니다.'], 404);
            }

            // 신고 상태 업데이트
            DB::table('reports')->where('id', $id)->update([
                'status'          => 'resolved',
                'resolved_action' => $request->action,
                'reviewed_by'     => auth()->id(),
                'updated_at'      => now(),
            ]);

            // 액션 실행
            switch ($request->action) {
                case 'hide':
                    $this->hideReportedContent($report->reportable_type, $report->reportable_id);
                    break;
                case 'delete':
                    $this->deleteReportedContent($report->reportable_type, $report->reportable_id);
                    break;
                case 'ban_user':
                    $this->banContentAuthor($report->reportable_type, $report->reportable_id);
                    break;
            }

            return response()->json(['message' => '신고가 처리되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['error' => '처리 실패: ' . $e->getMessage()], 500);
        }
    }

    private function hideReportedContent($type, $id)
    {
        $table = $this->getTableFromType($type);
        if ($table) {
            DB::table($table)->where('id', $id)->update(['status' => 'hidden']);
        }
    }

    private function deleteReportedContent($type, $id)
    {
        $table = $this->getTableFromType($type);
        if ($table) {
            DB::table($table)->where('id', $id)->delete();
        }
    }

    private function banContentAuthor($type, $id)
    {
        $table = $this->getTableFromType($type);
        if ($table) {
            $content = DB::table($table)->where('id', $id)->first();
            $userIdCol = 'user_id';
            if ($content && isset($content->$userIdCol)) {
                User::where('id', $content->$userIdCol)->update(['status' => 'banned']);
            }
        }
    }

    private function getTableFromType($type)
    {
        // reportable_type은 모델 클래스명 또는 짧은 이름
        $map = [
            'App\\Models\\Post'       => 'posts',
            'App\\Models\\Comment'    => 'comments',
            'App\\Models\\MarketItem' => 'market_items',
            'App\\Models\\JobPost'    => 'jobs',
            'App\\Models\\Business'   => 'businesses',
            'post'                    => 'posts',
            'comment'                 => 'comments',
            'market_item'             => 'market_items',
            'job'                     => 'jobs',
        ];
        return $map[$type] ?? null;
    }

    // ─── 보안: 봇 활동 로그 ──────────────────────────────────────

    public function botActivity(Request $request)
    {
        try {
            $q = DB::table('ip_bans')
                ->where('reason', 'like', '%자동%')
                ->orderByDesc('created_at');

            $logs = $q->paginate(25);

            $stats = [
                'total_auto'     => DB::table('ip_bans')->where('reason', 'like', '%자동%')->count(),
                'last_hour'      => DB::table('ip_bans')
                    ->where('reason', 'like', '%자동%')
                    ->where('created_at', '>=', now()->subHour())
                    ->count(),
                'last_24h'       => DB::table('ip_bans')
                    ->where('reason', 'like', '%자동%')
                    ->where('created_at', '>=', now()->subDay())
                    ->count(),
                'honeypot_count' => DB::table('ip_bans')
                    ->where('reason', 'like', '%Honeypot%')
                    ->count(),
                'rate_limit_count' => DB::table('ip_bans')
                    ->where('reason', 'like', '%글쓰기%')
                    ->count(),
            ];

            return response()->json(['logs' => $logs, 'stats' => $stats]);
        } catch (\Exception $e) {
            return response()->json([
                'logs'  => ['data' => [], 'total' => 0],
                'stats' => ['total_auto' => 0, 'last_hour' => 0, 'last_24h' => 0, 'honeypot_count' => 0, 'rate_limit_count' => 0],
            ]);
        }
    }
}