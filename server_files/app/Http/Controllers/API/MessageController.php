<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Message;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class MessageController extends Controller
{
    public function inbox()
    {
        $messages = Message::where('receiver_id', Auth::id())
            ->whereIn('status', ['active', 'deleted_by_sender'])
            ->with('sender:id,name,username,avatar')
            ->orderByDesc('created_at')
            ->paginate(20);
        return response()->json($messages);
    }

    public function send(Request $request)
    {
        $request->validate([
            'receiver_id' => 'required|exists:users,id',
            'content'     => 'required|string|max:2000',
        ]);
        if ($request->receiver_id == Auth::id()) {
            return response()->json(['message' => '자신에게는 메시지를 보낼 수 없습니다.'], 400);
        }
        $message = Message::create([
            'sender_id'   => Auth::id(),
            'receiver_id' => $request->receiver_id,
            'content'     => $request->content,
        ]);
        return response()->json(['message' => '메시지를 보냈습니다.', 'data' => $message], 201);
    }

    public function show(Message $message)
    {
        if ($message->receiver_id !== Auth::id() && $message->sender_id !== Auth::id()) abort(403);
        if ($message->receiver_id === Auth::id() && !$message->is_read) {
            $message->update(['is_read' => true, 'read_at' => now()]);
        }
        return response()->json($message->load(['sender:id,name,username,avatar', 'receiver:id,name,username,avatar']));
    }

    public function unreadCount()
    {
        $count = Message::where('receiver_id', Auth::id())->where('is_read', false)->count();
        return response()->json(['unread_count' => $count]);
    }
}
