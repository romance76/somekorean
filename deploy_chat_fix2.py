import paramiko
import os
import sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:80]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {remote_path}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

def write_remote(remote_path, content):
    import io
    f = io.BytesIO(content.encode('utf-8'))
    sftp.putfo(f, remote_path)
    sys.stdout.buffer.write(f'  WR: {remote_path}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== Chat Fix v2 ===')

# ── 1. Fix ChatController (nickname→username, profile_photo→avatar) ──────────
print('\n[1] Fix ChatController...')
chat_controller = r'''<?php

namespace App\Http\Controllers\API;

use App\Events\MessageSent;
use App\Http\Controllers\Controller;
use App\Models\ChatMessage;
use App\Models\ChatRoom;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class ChatController extends Controller
{
    public function rooms()
    {
        $rooms = ChatRoom::where('is_open', true)
            ->orderBy('type')
            ->orderBy('name')
            ->get();

        return response()->json($rooms);
    }

    public function room($slug)
    {
        $room = ChatRoom::where('slug', $slug)->firstOrFail();
        $messages = ChatMessage::where('chat_room_id', $room->id)
            ->with('user:id,name,username,avatar')
            ->latest()
            ->limit(60)
            ->get()
            ->reverse()
            ->values();

        return response()->json([
            'room'     => $room,
            'messages' => $messages,
        ]);
    }

    public function messages($slug, Request $request)
    {
        $room = ChatRoom::where('slug', $slug)->firstOrFail();
        $messages = ChatMessage::where('chat_room_id', $room->id)
            ->with('user:id,name,username,avatar')
            ->orderBy('id', 'desc')
            ->paginate(50);

        return response()->json($messages);
    }

    public function send(Request $request, $slug)
    {
        $request->validate(['message' => 'required|string|max:1000']);

        $room = ChatRoom::where('slug', $slug)->firstOrFail();

        $msg = ChatMessage::create([
            'chat_room_id' => $room->id,
            'user_id'      => Auth::id(),
            'message'      => $request->message,
            'type'         => 'text',
        ]);

        $msg->load('user:id,name,username,avatar');

        broadcast(new MessageSent($msg))->toOthers();

        return response()->json($msg, 201);
    }
}
'''
write_remote(f'{APP}/app/Http/Controllers/API/ChatController.php', chat_controller)

# ── 2. Fix MessageSent event (nickname→username, profile_photo→avatar) ───────
print('\n[2] Fix MessageSent event...')
message_sent = r'''<?php

namespace App\Events;

use App\Models\ChatMessage;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class MessageSent implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(public ChatMessage $message)
    {
    }

    public function broadcastOn(): array
    {
        return [
            new Channel('chat.' . $this->message->chat_room_id),
        ];
    }

    public function broadcastAs(): string
    {
        return 'message.sent';
    }

    public function broadcastWith(): array
    {
        return [
            'id'         => $this->message->id,
            'user_id'    => $this->message->user_id,
            'message'    => $this->message->message,
            'type'       => $this->message->type,
            'created_at' => $this->message->created_at->toISOString(),
            'user'       => [
                'id'       => $this->message->user->id,
                'name'     => $this->message->user->name,
                'username' => $this->message->user->username,
                'avatar'   => $this->message->user->avatar,
            ],
        ];
    }
}
'''
write_remote(f'{APP}/app/Events/MessageSent.php', message_sent)

# ── 3. Fix bootstrap/app.php (add channels routing) ──────────────────────────
print('\n[3] Fix bootstrap/app.php (add channels)...')
bootstrap_app = r'''<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        channels: __DIR__.'/../routes/channels.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->alias([
            'admin' => \App\Http\Middleware\AdminMiddleware::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
'''
write_remote(f'{APP}/bootstrap/app.php', bootstrap_app)

# ── 4. Upload fixed ChatRoom.vue ──────────────────────────────────────────────
print('\n[4] Upload ChatRoom.vue...')
upload(os.path.join(LOCAL,'resources','js','pages','chat','ChatRoom.vue'),
       f'{APP}/resources/js/pages/chat/ChatRoom.vue')

# ── 5. Fix nginx proxy_read_timeout for WebSocket ────────────────────────────
print('\n[5] Fix nginx WebSocket timeout...')
run(r"""sed -i 's|proxy_cache_bypass \$http_upgrade;|proxy_cache_bypass $http_upgrade;\n        proxy_read_timeout 3600;\n        proxy_send_timeout 3600;\n        keepalive_timeout 3600;|' /etc/nginx/sites-available/somekorean""")
run('nginx -t 2>&1')
run('systemctl reload nginx 2>&1')

# ── 6. Clear caches ───────────────────────────────────────────────────────────
print('\n[6] Clear caches...')
run(f'cd {APP} && php8.2 artisan config:clear && php8.2 artisan route:clear && php8.2 artisan cache:clear 2>&1')

# ── 7. Verify broadcast route registered ─────────────────────────────────────
print('\n[7] Check broadcast routes...')
run(f'cd {APP} && php8.2 artisan route:list 2>/dev/null | grep broadcast')

# ── 8. Build ──────────────────────────────────────────────────────────────────
print('\n[8] Building frontend...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# ── 9. Final check ────────────────────────────────────────────────────────────
print('\n[9] Final check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')
run(f'curl -s "https://somekorean.com/broadcasting/auth" -o /dev/null -w "%{{http_code}}"')

sftp.close()
client.close()
print('\n=== Chat Fix v2 DONE ===')
