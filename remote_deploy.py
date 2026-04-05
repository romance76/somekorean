import paramiko
import sys

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return out, err, exit_code

def write_file(sftp, path, content):
    with sftp.open(path, 'w') as f:
        f.write(content)
    print(f"  Written: {path}")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')
sftp = ssh.open_sftp()

JWT_SECRET = 'SlmpUXOldW0YTu1S53biybEeQS4fhotiS6DNiFiUeq6tafXJumU6izOJon1EvEMZ'

# ══════════════════════════════════════════════
# 1. Socket.io server
# ══════════════════════════════════════════════
print("=== 1. Creating socket-server ===")
run(ssh, "mkdir -p /var/www/somekorean/socket-server")

# package.json
write_file(sftp, '/var/www/somekorean/socket-server/package.json', '''{
  "name": "somekorean-socket",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "socket.io": "^4.7.0",
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "jsonwebtoken": "^9.0.0"
  }
}
''')

# server.js
server_js = r"""const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: ['https://somekorean.com', 'http://localhost:5173'], credentials: true }
});

const JWT_SECRET = process.env.JWT_SECRET || '""" + JWT_SECRET + r"""';

// 연결된 유저 관리
const connectedUsers = new Map(); // userId -> Set of socket ids

// JWT 인증 미들웨어
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) return next(new Error('인증 필요'));
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    socket.userId = String(decoded.sub || decoded.id);
    next();
  } catch(e) {
    next(new Error('토큰 만료'));
  }
});

io.on('connection', (socket) => {
  const userId = socket.userId;
  console.log(`User ${userId} connected (${socket.id})`);

  if (!connectedUsers.has(userId)) connectedUsers.set(userId, new Set());
  connectedUsers.get(userId).add(socket.id);

  io.emit('user:online', { userId });

  socket.on('disconnect', () => {
    const sockets = connectedUsers.get(userId);
    if (sockets) {
      sockets.delete(socket.id);
      if (sockets.size === 0) {
        connectedUsers.delete(userId);
        io.emit('user:offline', { userId });
      }
    }
    console.log(`User ${userId} disconnected`);
  });

  // ─── 노인안심 이벤트 ─────────────────────
  socket.on('elder:checkin', (data) => {
    console.log(`Elder checkin from user ${userId}`);
    if (data.guardianUserId) {
      sendToUser(data.guardianUserId, 'elder:checkin-done', {
        elderId: userId,
        checkedAt: new Date().toISOString()
      });
    }
  });

  socket.on('elder:sos', (data) => {
    console.log(`SOS from user ${userId}!`);
    if (data.guardianUserId) {
      sendToUser(data.guardianUserId, 'elder:sos-alert', {
        elderId: userId,
        elderName: data.elderName,
        lat: data.lat,
        lng: data.lng,
        time: new Date().toISOString()
      });
    }
  });

  socket.on('elder:sos-resolve', (data) => {
    if (data.elderUserId) {
      sendToUser(data.elderUserId, 'elder:sos-resolved', {
        resolvedBy: userId,
        time: new Date().toISOString()
      });
    }
  });

  // ─── WebRTC 시그널링 ─────────────────────
  socket.on('webrtc:offer', (data) => {
    sendToUser(data.targetUserId, 'webrtc:offer', {
      from: userId, offer: data.offer, callType: data.callType
    });
  });

  socket.on('webrtc:answer', (data) => {
    sendToUser(data.targetUserId, 'webrtc:answer', {
      from: userId, answer: data.answer
    });
  });

  socket.on('webrtc:ice-candidate', (data) => {
    sendToUser(data.targetUserId, 'webrtc:ice-candidate', {
      from: userId, candidate: data.candidate
    });
  });

  socket.on('webrtc:hangup', (data) => {
    sendToUser(data.targetUserId, 'webrtc:hangup', { from: userId });
  });

  // ─── 일반 알림 ─────────────────────────
  socket.on('notification', (data) => {
    if (data.targetUserId) {
      sendToUser(data.targetUserId, 'notification', data);
    }
  });
});

function sendToUser(userId, event, data) {
  const sockets = connectedUsers.get(String(userId));
  if (sockets) {
    sockets.forEach(sid => io.to(sid).emit(event, data));
    return true;
  }
  return false;
}

// Laravel에서 호출할 수 있는 REST API
app.use(express.json());

app.post('/send-notification', (req, res) => {
  const { userId, event, data } = req.body;
  const sent = sendToUser(String(userId), event || 'notification', data || {});
  res.json({ sent, online: connectedUsers.has(String(userId)) });
});

app.get('/online/:userId', (req, res) => {
  res.json({ online: connectedUsers.has(req.params.userId) });
});

app.get('/online-users', (req, res) => {
  res.json({ users: Array.from(connectedUsers.keys()), count: connectedUsers.size });
});

const PORT = process.env.SOCKET_PORT || 3001;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Socket.io server running on port ${PORT}`);
});
"""

write_file(sftp, '/var/www/somekorean/socket-server/server.js', server_js)

# npm install
print("  Installing npm packages...")
out, err, code = run(ssh, "cd /var/www/somekorean/socket-server && npm install 2>&1", timeout=120)
print(f"  npm install exit={code}")
if out: print(out[-500:])

# ══════════════════════════════════════════════
# 2. PM2 setup
# ══════════════════════════════════════════════
print("\n=== 2. PM2 setup ===")
out, err, code = run(ssh, "which pm2 2>/dev/null || npm install -g pm2 2>&1")
print(f"  pm2 install: exit={code}")
if out: print(out[-300:])

# Stop existing if any
run(ssh, "pm2 delete somekorean-socket 2>/dev/null")

out, err, code = run(ssh, "cd /var/www/somekorean/socket-server && pm2 start server.js --name somekorean-socket 2>&1")
print(f"  pm2 start: exit={code}")
if out: print(out[-500:])

out, err, code = run(ssh, "pm2 save 2>&1")
print(f"  pm2 save: exit={code}")

out, err, code = run(ssh, "pm2 startup 2>&1")
print(f"  pm2 startup: exit={code}")

# ══════════════════════════════════════════════
# 3. Nginx WebSocket proxy
# ══════════════════════════════════════════════
print("\n=== 3. Nginx config ===")
out, err, code = run(ssh, "cat /etc/nginx/sites-available/somekorean")
nginx_conf = out

if '/socket.io/' not in nginx_conf:
    # Add socket.io location before the first location block
    new_block = """    # WebSocket proxy for Socket.io
    location /socket.io/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

"""
    # Insert before the first location block
    insert_point = nginx_conf.find("    location /app {")
    if insert_point == -1:
        insert_point = nginx_conf.find("    location /")

    if insert_point > 0:
        new_conf = nginx_conf[:insert_point] + new_block + nginx_conf[insert_point:]
        # Backup first
        run(ssh, "cp /etc/nginx/sites-available/somekorean /etc/nginx/sites-available/somekorean.bak2")
        write_file(sftp, '/etc/nginx/sites-available/somekorean', new_conf)
        print("  Added socket.io location block")
    else:
        print("  ERROR: Could not find insertion point in nginx config")
else:
    print("  socket.io location already exists")

out, err, code = run(ssh, "nginx -t 2>&1")
print(f"  nginx -t: {out}{err}")
if code == 0:
    out, err, code = run(ssh, "systemctl reload nginx 2>&1")
    print(f"  nginx reload: exit={code}")
else:
    print("  SKIPPING nginx reload due to config error")

# ══════════════════════════════════════════════
# 4. PWA - Update sw.js with push notification support
# ══════════════════════════════════════════════
print("\n=== 4. PWA updates ===")

sw_js = r"""const CACHE_NAME = 'somekorean-v2';
const STATIC_ASSETS = ['/', '/manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

// 푸시 알림 수신
self.addEventListener('push', (event) => {
  let data = { title: 'SomeKorean', body: '새 알림이 있습니다', icon: '/icons/icon-192x192.png' };
  if (event.data) {
    try { data = { ...data, ...event.data.json() }; } catch(err) { data.body = event.data.text(); }
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || '/icons/icon-192x192.png',
      badge: '/icons/icon-192x192.png',
      vibrate: [200, 100, 200],
      data: data.url ? { url: data.url } : {},
      actions: data.actions || []
    })
  );
});

// 알림 클릭
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      for (const client of windowClients) {
        if (client.url.includes('somekorean.com') && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      return clients.openWindow(url);
    })
  );
});
"""
write_file(sftp, '/var/www/somekorean/public/sw.js', sw_js)

# Create PWA icons directory and placeholder icons
print("  Creating PWA icons...")
run(ssh, "mkdir -p /var/www/somekorean/public/icons")

# Generate simple placeholder PNG icons using Python on the server
icon_script = r"""
import struct, zlib

def create_png(size, filename):
    # Simple blue circle icon
    width = height = size
    center = size // 2
    radius = int(size * 0.4)

    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter byte
        for x in range(width):
            dx = x - center
            dy = y - center
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < radius:
                # Blue gradient
                r, g, b, a = 37, 99, 235, 255
                if dist > radius - 2:
                    a = int(255 * (radius - dist) / 2)
                raw += bytes([r, g, b, a])
            else:
                raw += b'\x00\x00\x00\x00'

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', zlib.compress(raw)))
        f.write(chunk(b'IEND', b''))

for sz in [72, 96, 128, 192, 512]:
    create_png(sz, f'/var/www/somekorean/public/icons/icon-{sz}x{sz}.png')
    print(f'Created icon-{sz}x{sz}.png')
"""
write_file(sftp, '/tmp/gen_icons.py', icon_script)
out, err, code = run(ssh, "python3 /tmp/gen_icons.py 2>&1")
print(f"  Icons: {out}")

# ══════════════════════════════════════════════
# 5. Update blade template
# ══════════════════════════════════════════════
print("\n=== 5. Blade template ===")
out, err, code = run(ssh, "cat /var/www/somekorean/resources/views/welcome.blade.php")
blade = out

if 'manifest' not in blade:
    blade = blade.replace(
        '</head>',
        '    <link rel="manifest" href="/manifest.json">\n    <meta name="theme-color" content="#2563eb">\n</head>'
    )
    write_file(sftp, '/var/www/somekorean/resources/views/welcome.blade.php', blade)
    print("  Added manifest link to blade")
else:
    print("  Manifest already in blade")

# ══════════════════════════════════════════════
# 6. Install socket.io-client + create useSocket composable
# ══════════════════════════════════════════════
print("\n=== 6. Vue socket client ===")
out, err, code = run(ssh, "cd /var/www/somekorean && npm install socket.io-client 2>&1", timeout=120)
print(f"  npm install socket.io-client: exit={code}")
if out: print(out[-300:])

# useSocket.js composable
use_socket_js = r"""import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

let socket = null
const isConnected = ref(false)
const connectionError = ref(null)

export function useSocket() {
  function connect() {
    if (socket?.connected) return
    const token = localStorage.getItem('sk_token')
    if (!token) return

    socket = io(window.location.origin, {
      path: '/socket.io/',
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    })

    socket.on('connect', () => {
      isConnected.value = true
      connectionError.value = null
      console.log('[Socket] Connected')
    })

    socket.on('disconnect', (reason) => {
      isConnected.value = false
      console.log('[Socket] Disconnected:', reason)
    })

    socket.on('connect_error', (err) => {
      connectionError.value = err.message
      console.error('[Socket] Connection error:', err.message)
    })
  }

  function disconnect() {
    if (socket) {
      socket.disconnect()
      socket = null
      isConnected.value = false
    }
  }

  function emit(event, data) {
    if (socket?.connected) socket.emit(event, data)
  }

  function on(event, callback) {
    if (socket) socket.on(event, callback)
  }

  function off(event, callback) {
    if (socket) socket.off(event, callback)
  }

  return { socket: () => socket, isConnected, connectionError, connect, disconnect, emit, on, off }
}
"""
write_file(sftp, '/var/www/somekorean/resources/js/composables/useSocket.js', use_socket_js)

# ══════════════════════════════════════════════
# 7. Update app.js to register service worker + connect socket
# ══════════════════════════════════════════════
print("\n=== 7. Update app.js ===")
out, err, code = run(ssh, "cat /var/www/somekorean/resources/js/app.js")
app_js = out

# Add service worker registration and socket connection after the existing code
sw_and_socket_code = """
// ─── Service Worker 등록 (PWA 푸시 알림) ─────────────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').then(reg => {
    console.log('[SW] Registered:', reg.scope);
  }).catch(err => {
    console.error('[SW] Registration failed:', err);
  });
}

// ─── Socket.io 실시간 연결 ─────────────────────────────
import { useSocket } from './composables/useSocket'
import { watch } from 'vue'

const { connect: socketConnect } = useSocket();

// 로그인 상태면 소켓 연결
watch(() => authStore.isLoggedIn, (loggedIn) => {
  if (loggedIn) socketConnect();
}, { immediate: true });
"""

if 'serviceWorker' not in app_js:
    app_js += sw_and_socket_code
    write_file(sftp, '/var/www/somekorean/resources/js/app.js', app_js)
    print("  Added SW + Socket to app.js")
else:
    print("  SW already in app.js")

# ══════════════════════════════════════════════
# 8. Update ElderCheckCommand.php to call socket server
# ══════════════════════════════════════════════
print("\n=== 8. Update ElderCheckCommand ===")
out, err, code = run(ssh, "cat /var/www/somekorean/app/Console/Commands/ElderCheckCommand.php")
elder_cmd = out

if 'send-notification' not in elder_cmd:
    # Add Http import if not exists
    if 'use Illuminate\\Support\\Facades\\Http;' not in elder_cmd:
        elder_cmd = elder_cmd.replace(
            'use Illuminate\\Support\\Facades\\DB;',
            'use Illuminate\\Support\\Facades\\DB;\nuse Illuminate\\Support\\Facades\\Http;'
        )

    # Add socket notification call in sendGuardianAlert method
    socket_call = """
        // 소켓 서버에 실시간 알림 전송
        try {
            if ($setting->guardian_user_id) {
                Http::timeout(3)->post('http://127.0.0.1:3001/send-notification', [
                    'userId' => (string) $setting->guardian_user_id,
                    'event'  => 'elder:checkin-missed',
                    'data'   => [
                        'elderId'   => $setting->user_id,
                        'elderName' => $userName,
                        'message'   => "{$userName}님이 체크인에 응답하지 않았습니다",
                        'alertType' => $alertType,
                        'time'      => now()->toISOString(),
                    ],
                ]);
            }
        } catch (\\Exception $e) {
            // 소켓 서버 다운 시 무시 (DB 알림은 이미 전송됨)
        }
"""
    # Insert after the last Notification::create in sendGuardianAlert
    insert_marker = "        // Notify the elder user"
    if insert_marker in elder_cmd:
        elder_cmd = elder_cmd.replace(insert_marker, socket_call + "\n" + insert_marker)
        write_file(sftp, '/var/www/somekorean/app/Console/Commands/ElderCheckCommand.php', elder_cmd)
        print("  Added socket notification to ElderCheckCommand")
    else:
        print("  WARNING: Could not find insertion point in ElderCheckCommand")
else:
    print("  Socket notification already in ElderCheckCommand")

# ══════════════════════════════════════════════
# 9. Build
# ══════════════════════════════════════════════
print("\n=== 9. npm run build ===")
out, err, code = run(ssh, "cd /var/www/somekorean && npm run build 2>&1", timeout=180)
lines = out.strip().split('\n')
print('\n'.join(lines[-15:]))
print(f"  Build exit code: {code}")
if err:
    err_lines = err.strip().split('\n')
    print('\n'.join(err_lines[-10:]))

# ══════════════════════════════════════════════
# 10. Verify
# ══════════════════════════════════════════════
print("\n=== 10. Verification ===")
out, err, code = run(ssh, "pm2 status 2>&1")
print(f"PM2 Status:\n{out}")

out, err, code = run(ssh, "curl -s http://127.0.0.1:3001/online-users 2>&1")
print(f"Socket server test: {out}")

out, err, code = run(ssh, "curl -s -o /dev/null -w '%{http_code}' https://somekorean.com/socket.io/?EIO=4\\&transport=polling 2>&1")
print(f"External socket.io test (HTTP code): {out}")

sftp.close()
ssh.close()
print("\n=== Done! ===")
