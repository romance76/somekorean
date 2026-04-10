<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\{ChatRoom, ChatRoomUser, ChatMessage};
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ChatController extends Controller
{
    public function rooms() {
        $userId = auth()->id();
        $roomIds = ChatRoomUser::where('user_id', $userId)->pluck('chat_room_id');

        // 차단된 방 제외
        $bannedRoomIds = DB::table('chat_room_bans')->where('user_id', $userId)->pluck('chat_room_id');
        $roomIds = $roomIds->diff($bannedRoomIds);

        $rooms = ChatRoom::whereIn('id', $roomIds)->with(['messages' => fn($q) => $q->latest()->limit(1)])->get();
        return response()->json(['success'=>true,'data'=>$rooms]);
    }

    public function createRoom(Request $request) {
        $room = ChatRoom::create(['name'=>$request->name,'type'=>$request->type??'dm','created_by'=>auth()->id()]);
        ChatRoomUser::create(['chat_room_id'=>$room->id,'user_id'=>auth()->id()]);
        if ($request->user_id) ChatRoomUser::create(['chat_room_id'=>$room->id,'user_id'=>$request->user_id]);
        return response()->json(['success'=>true,'data'=>$room],201);
    }

    public function messages($id) {
        // 차단된 유저는 메시지 조회 불가
        $banned = DB::table('chat_room_bans')->where('chat_room_id', $id)->where('user_id', auth()->id())->exists();
        if ($banned) return response()->json(['success'=>false,'message'=>'이 채팅방에서 차단되었습니다.'], 403);

        $messages = ChatMessage::with('user:id,name,nickname,avatar')->where('chat_room_id',$id)->orderByDesc('created_at')->paginate(50);
        return response()->json(['success'=>true,'data'=>$messages]);
    }

    public function sendMessage(Request $request, $id) {
        $request->validate(['content' => 'required']);

        // 차단된 유저는 메시지 전송 불가
        $banned = DB::table('chat_room_bans')->where('chat_room_id', $id)->where('user_id', auth()->id())->exists();
        if ($banned) return response()->json(['success'=>false,'message'=>'이 채팅방에서 차단되었습니다.'], 403);

        $msg = ChatMessage::create(['chat_room_id'=>$id,'user_id'=>auth()->id(),'content'=>$request->content,'type'=>$request->type??'text']);

        // 실시간 브로드캐스트
        try { event(new \App\Events\MessageSent($msg->load('user:id,name,nickname,avatar'))); } catch (\Exception $e) {}
        return response()->json(['success'=>true,'data'=>$msg->load('user:id,name,nickname,avatar')],201);
    }
}
