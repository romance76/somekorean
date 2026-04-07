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
        $result = $friends->map(function($f) use ($userId) {
            $otherId = $f->user_id == $userId ? $f->friend_id : $f->user_id;
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
                'created_at' => $f->created_at,
            ];
        })->filter()->values();

        return response()->json(['success' => true, 'data' => $result]);
    }

    public function sendRequest(Request $request, $userId) {
        if ($userId == auth()->id()) return response()->json(['success' => false, 'message' => '자신에게 요청할 수 없습니다'], 400);
        if (Friend::where('user_id', auth()->id())->where('friend_id', $userId)->exists())
            return response()->json(['success' => false, 'message' => '이미 요청했습니다'], 400);

        Friend::create([
            'user_id' => auth()->id(),
            'friend_id' => $userId,
            'status' => 'pending',
            'source' => $request->source ?? 'community',
        ]);
        return response()->json(['success' => true, 'message' => '친구 요청을 보냈습니다']);
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
