<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\Friend;
use App\Models\User;
use Illuminate\Http\Request;

class FriendController extends Controller
{
    // 전체 친구 목록 (모든 상태 + 온라인 정보)
    public function index(Request $request) {
        $userId = auth()->id();

        // 만료된 pending 요청 자동 삭제
        Friend::where('status', 'pending')
            ->whereNotNull('expires_at')->where('expires_at', '<', now())
            ->where(function($q) use ($userId) {
                $q->where('user_id', $userId)->orWhere('friend_id', $userId);
            })->delete();

        $query = Friend::query()
            ->where(function($q) use ($userId) {
                $q->where('user_id', $userId)->orWhere('friend_id', $userId);
            });

        // source 필터
        if ($request->source) $query->where('source', $request->source);
        // status 필터
        if ($request->status) $query->where('status', $request->status);

        $friends = $query->get();

        // 관련 유저 정보 + 온라인 상태 추가
        // 양방향 레코드 중복 제거 (같은 상대방이 2번 나오는 것 방지)
        $seenIds = [];
        $result = $friends->map(function($f) use ($userId, &$seenIds) {
            $otherId = $f->user_id == $userId ? $f->friend_id : $f->user_id;
            if (in_array($otherId, $seenIds)) return null; // 중복 스킵
            $seenIds[] = $otherId;
            $isSender = $f->user_id == $userId; // 내가 보낸 건지
            $other = User::select('id','name','nickname','avatar','city','state','bio','last_active_at')->find($otherId);
            if (!$other) return null;

            // 온라인 상태
            $status = 'offline';
            if ($other->last_active_at) {
                $mins = now()->diffInMinutes($other->last_active_at);
                if ($mins <= 5) $status = 'online';
                elseif ($mins <= 30) $status = 'away';
            }

            return [
                'id' => $f->id,
                'friend' => $other,
                'status' => $f->status,
                'source' => $f->source,
                'online_status' => $status,
                'is_sender' => $isSender,
                'can_cancel' => $isSender && $f->canCancel(),
                'expires_at' => $f->expires_at,
                'created_at' => $f->created_at,
            ];
        })->filter()->values();

        return response()->json(['success' => true, 'data' => $result]);
    }

    public function sendRequest(Request $request, $userId) {
        if ($userId == auth()->id()) return response()->json(['success' => false, 'message' => '자신에게 요청할 수 없습니다'], 400);
        $target = User::find($userId);
        if (!$target) return response()->json(['success' => false, 'message' => '사용자를 찾을 수 없습니다'], 404);
        if (!$target->allow_friend_request) return response()->json(['success' => false, 'message' => '이 사용자는 친구 요청을 받지 않습니다'], 403);

        // 만료된 요청 자동 삭제 (양방향)
        Friend::where('status', 'pending')->whereNotNull('expires_at')->where('expires_at', '<', now())
            ->where(function($q) use ($userId) {
                $q->where(function($q2) use ($userId) {
                    $q2->where('user_id', auth()->id())->where('friend_id', $userId);
                })->orWhere(function($q2) use ($userId) {
                    $q2->where('user_id', $userId)->where('friend_id', auth()->id());
                });
            })->delete();

        // 내가 이미 보낸 요청 체크
        $existing = Friend::where('user_id', auth()->id())->where('friend_id', $userId)->first();
        if ($existing) {
            if ($existing->status === 'accepted') return response()->json(['success' => false, 'message' => '이미 친구입니다'], 400);
            return response()->json(['success' => false, 'message' => '이미 요청했습니다'], 400);
        }

        // 상대방이 나에게 보낸 pending 요청이 있으면 → 자동 수락
        $reverse = Friend::where('user_id', $userId)->where('friend_id', auth()->id())->where('status', 'pending')->first();
        if ($reverse) {
            $reverse->update(['status' => 'accepted', 'expires_at' => null]);
            Friend::firstOrCreate(
                ['user_id' => auth()->id(), 'friend_id' => $userId],
                ['status' => 'accepted', 'source' => $request->source ?? 'community']
            );
            return response()->json(['success' => true, 'message' => '서로 친구가 되었습니다!', 'auto_accepted' => true]);
        }

        // 이미 친구인지 체크 (역방향 accepted)
        $reverseAccepted = Friend::where('user_id', $userId)->where('friend_id', auth()->id())->where('status', 'accepted')->first();
        if ($reverseAccepted) return response()->json(['success' => false, 'message' => '이미 친구입니다'], 400);

        $friend = Friend::create([
            'user_id' => auth()->id(),
            'friend_id' => $userId,
            'status' => 'pending',
            'source' => $request->source ?? 'community',
            'expires_at' => now()->addDays(7),
        ]);
        return response()->json(['success' => true, 'message' => '친구 요청을 보냈습니다', 'data' => $friend]);
    }

    public function cancelRequest($id) {
        $req = Friend::where('user_id', auth()->id())->where('id', $id)->where('status', 'pending')->firstOrFail();

        if ($req->created_at->diffInHours(now()) < 24) {
            return response()->json([
                'success' => false,
                'message' => '요청 후 24시간이 지나야 취소할 수 있습니다.',
                'can_cancel_at' => $req->created_at->addHours(24)->toISOString(),
            ], 403);
        }

        $req->delete();
        return response()->json(['success' => true, 'message' => '친구 요청을 취소했습니다']);
    }

    public function accept($id) {
        $req = Friend::where('friend_id', auth()->id())->where('id', $id)->where('status', 'pending')->firstOrFail();
        $req->update(['status' => 'accepted']);
        // 양방향 친구 관계 생성
        Friend::firstOrCreate(
            ['user_id' => auth()->id(), 'friend_id' => $req->user_id],
            ['status' => 'accepted', 'source' => $req->source]
        );
        return response()->json(['success' => true, 'message' => '친구 요청을 수락했습니다']);
    }

    public function block($userId) {
        Friend::updateOrCreate(['user_id' => auth()->id(), 'friend_id' => $userId], ['status' => 'blocked']);
        return response()->json(['success' => true]);
    }

    public function remove($id) {
        $f = Friend::findOrFail($id);
        // 양방향 삭제
        Friend::where('user_id', $f->user_id)->where('friend_id', $f->friend_id)->delete();
        Friend::where('user_id', $f->friend_id)->where('friend_id', $f->user_id)->delete();
        return response()->json(['success' => true]);
    }

    // 프라이빗 1:1 채팅방 생성/조회
    public function createPrivateChat(Request $request) {
        $request->validate(['friend_id' => 'required|integer']);
        $userId = auth()->id();
        $friendId = $request->friend_id;

        // 기존 1:1 채팅방 찾기
        $existing = \DB::table('chat_room_members as m1')
            ->join('chat_room_members as m2', 'm1.room_id', '=', 'm2.room_id')
            ->join('chat_rooms', 'chat_rooms.id', '=', 'm1.room_id')
            ->where('m1.user_id', $userId)
            ->where('m2.user_id', $friendId)
            ->where('chat_rooms.is_private', true)
            ->select('chat_rooms.id')
            ->first();

        if ($existing) return response()->json(['success' => true, 'data' => ['room_id' => $existing->id]]);

        // 새로 생성
        $friend = User::find($friendId);
        $room = \App\Models\ChatRoom::create([
            'name' => auth()->user()->name . ' & ' . ($friend->name ?? ''),
            'type' => 'private',
            'is_private' => true,
            'created_by' => $userId,
        ]);
        \DB::table('chat_room_members')->insert([
            ['room_id' => $room->id, 'user_id' => $userId, 'joined_at' => now()],
            ['room_id' => $room->id, 'user_id' => $friendId, 'joined_at' => now()],
        ]);

        return response()->json(['success' => true, 'data' => ['room_id' => $room->id]]);
    }

    // 그룹 채팅방 생성
    public function createGroupChat(Request $request) {
        $request->validate(['name' => 'required|string|max:50', 'friend_ids' => 'required|array']);
        $userId = auth()->id();

        $room = \App\Models\ChatRoom::create([
            'name' => $request->name,
            'type' => 'group',
            'is_private' => true,
            'created_by' => $userId,
        ]);

        // 참여자 추가 (본인 포함)
        $members = [['room_id' => $room->id, 'user_id' => $userId, 'joined_at' => now()]];
        foreach ($request->friend_ids as $fid) {
            $members[] = ['room_id' => $room->id, 'user_id' => $fid, 'joined_at' => now()];
        }
        \DB::table('chat_room_members')->insert($members);

        return response()->json(['success' => true, 'data' => $room]);
    }

    // 내 프라이빗 채팅방 목록
    public function privateChatRooms() {
        $userId = auth()->id();
        $roomIds = \DB::table('chat_room_members')->where('user_id', $userId)->pluck('room_id');
        $rooms = \App\Models\ChatRoom::whereIn('id', $roomIds)->where('is_private', true)->get();

        $result = $rooms->map(function($room) use ($userId) {
            $memberIds = \DB::table('chat_room_members')->where('room_id', $room->id)->pluck('user_id');
            $members = User::whereIn('id', $memberIds)->select('id','name','nickname','avatar','last_active_at')->get();
            $lastMsg = \DB::table('chat_messages')->where('room_id', $room->id)->orderByDesc('created_at')->first();
            return [
                'id' => $room->id,
                'name' => $room->name,
                'type' => $room->type,
                'members' => $members,
                'last_message' => $lastMsg?->content,
                'last_message_at' => $lastMsg?->created_at,
            ];
        });

        return response()->json(['success' => true, 'data' => $result]);
    }
}
