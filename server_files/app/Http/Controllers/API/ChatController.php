<?php

namespace App\Http\Controllers\API;

use App\Events\MessageSent;
use App\Http\Controllers\Controller;
use App\Models\ChatMessage;
use App\Models\ChatRoom;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class ChatController extends Controller
{
    // 한국어 + 영어 금지어
    private const BANNED = [
        '씨발','시발','씨팔','시팔','개새끼','병신','지랄','미친놈','미친년','좆','보지','자지','창녀','걸레',
        '꺼져','죽어','ㅅㅂ','ㅂㅅ','ㅈㄹ','쌍년','쌍놈','개년','개놈','후레자식','18놈','18년','18새끼',
        '존나','존내','좃같','닥쳐','꺼지세요','개같','씹','ㅅㅂ','ㅂㅅ','ㅈㄱ','ㅁㅊ',
        'fuck','shit','bitch','asshole','bastard','cunt','nigger','faggot','whore','slut','damn you',
    ];

    private function filterProfanity(string $text): string
    {
        foreach (self::BANNED as $word) {
            $stars = str_repeat('*', mb_strlen($word));
            $text  = str_ireplace($word, $stars, $text);
        }
        return $text;
    }

    public function rooms()
    {
        $rooms = ChatRoom::where('is_open', true)
            ->orderBy('type')
            ->orderBy('name')
            ->get()
            ->map(function ($room) {
                $last = ChatMessage::where('chat_room_id', $room->id)
                    ->orderBy('id', 'desc')
                    ->select('id', 'message', 'created_at')
                    ->first();
                $room->last_message_id      = $last?->id ?? 0;
                $room->last_message_preview = $last ? mb_substr($last->message, 0, 30) : null;
                $room->last_message_at      = $last?->created_at;
                $room->unread_count         = 0; // 클라이언트에서 localStorage 기반 계산
                return $room;
            });
        return response()->json($rooms);
    }

    public function room($slug)
    {
        $room = ChatRoom::where('slug', $slug)->firstOrFail();

        $blockedIds = Auth::check()
            ? DB::table('user_blocks')->where('user_id', Auth::id())->pluck('blocked_user_id')->toArray()
            : [];

        $messages = ChatMessage::where('chat_room_id', $room->id)
            ->with('user:id,name,username,avatar')
            ->latest()
            ->limit(80)
            ->get()
            ->reverse()
            ->values();

        return response()->json([
            'room'        => $room,
            'messages'    => $messages,
            'blocked_ids' => $blockedIds,
        ]);
    }

    public function messages($slug, Request $request)
    {
        $room     = ChatRoom::where('slug', $slug)->firstOrFail();
        $messages = ChatMessage::where('chat_room_id', $room->id)
            ->with('user:id,name,username,avatar')
            ->orderBy('id', 'desc')
            ->paginate(50);
        return response()->json($messages);
    }

    public function send(Request $request, $slug)
    {
        $room = ChatRoom::where('slug', $slug)->firstOrFail();

        // 파일 업로드
        if ($request->hasFile('file')) {
            $request->validate(['file' => 'required|file|max:10240']); // 10MB
            $file     = $request->file('file');
            $path     = $file->store('chat', 'public');
            $fileType = str_starts_with($file->getMimeType(), 'image/') ? 'image' : 'file';

            $msg = ChatMessage::create([
                'chat_room_id' => $room->id,
                'user_id'      => Auth::id(),
                'message'      => $file->getClientOriginalName(),
                'file_url'     => Storage::url($path),
                'file_name'    => $file->getClientOriginalName(),
                'file_type'    => $fileType,
                'type'         => $fileType,
            ]);
        } else {
            $request->validate(['message' => 'required|string|max:1000']);
            $text = $this->filterProfanity($request->message);

            $msg = ChatMessage::create([
                'chat_room_id' => $room->id,
                'user_id'      => Auth::id(),
                'message'      => $text,
                'type'         => 'text',
            ]);
        }

        $msg->load('user:id,name,username,avatar');
        broadcast(new MessageSent($msg))->toOthers();
        return response()->json($msg, 201);
    }

    public function search(Request $request, $slug)
    {
        $room = ChatRoom::where('slug', $slug)->firstOrFail();
        $q    = $request->query('q', '');
        if (mb_strlen($q) < 2) return response()->json([]);

        $messages = ChatMessage::where('chat_room_id', $room->id)
            ->where('message', 'like', "%{$q}%")
            ->with('user:id,name,username,avatar')
            ->orderBy('id', 'desc')
            ->limit(30)
            ->get();

        return response()->json($messages);
    }

    public function blockUser($userId)
    {
        DB::table('user_blocks')->updateOrInsert(
            ['user_id' => Auth::id(), 'blocked_user_id' => $userId],
            ['created_at' => now(), 'updated_at' => now()]
        );
        return response()->json(['blocked' => true]);
    }

    public function unblockUser($userId)
    {
        DB::table('user_blocks')
            ->where('user_id', Auth::id())
            ->where('blocked_user_id', $userId)
            ->delete();
        return response()->json(['blocked' => false]);
    }

    public function reportMessage(Request $request, $messageId)
    {
        $request->validate(['reason' => 'nullable|string|max:100']);
        DB::table('chat_reports')->updateOrInsert(
            ['reporter_id' => Auth::id(), 'message_id' => $messageId],
            ['reason' => $request->reason ?? 'spam', 'created_at' => now(), 'updated_at' => now()]
        );
        return response()->json(['reported' => true]);
    }

    public function createRoom(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:100',
            'type' => 'in:public,friend,group',
        ]);

        $slug = \Illuminate\Support\Str::slug($request->name) . '-' . time();
        $room = ChatRoom::create([
            'name'       => $request->name,
            'slug'       => $slug,
            'type'       => $request->input('type', 'public'),
            'is_open'    => true,
            'created_by' => Auth::id(),
        ]);

        // 초대 유저 처리
        if ($request->has('invite_users') && is_array($request->invite_users)) {
            foreach ($request->invite_users as $uid) {
                try {
                    DB::table('notifications')->insert([
                        'user_id'    => $uid,
                        'type'       => 'chat_invite',
                        'data'       => json_encode(['room_id' => $room->id, 'room_name' => $room->name, 'slug' => $room->slug]),
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                } catch (\Exception $e) {}
            }
        }

        return response()->json($room, 201);
    }

    public function updateRoom(Request $request, $slug)
    {
        $room = \App\Models\ChatRoom::where('slug', $slug)->firstOrFail();
        if ($room->created_by !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 수정할 수 있습니다.'], 403);
        }
        $request->validate(['name' => 'required|string|max:100']);
        $room->update(['name' => $request->name]);
        return response()->json($room);
    }

    public function deleteRoom(Request $request, $slug)
    {
        $room = \App\Models\ChatRoom::where('slug', $slug)->firstOrFail();
        if ($room->created_by !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '방장만 삭제할 수 있습니다.'], 403);
        }
        // Delete messages first
        \Illuminate\Support\Facades\DB::table('chat_messages')->where('room_id', $room->id)->delete();
        $room->delete();
        return response()->json(['message' => '채팅방이 삭제되었습니다.']);
    }
}
