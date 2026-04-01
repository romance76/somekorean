const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');
const webpush = require('web-push');
const mysql = require('mysql2/promise');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: ['https://somekorean.com', 'http://localhost:5173'], credentials: true }
});

const JWT_SECRET = process.env.JWT_SECRET || 'SlmpUXOldW0YTu1S53biybEeQS4fhotiS6DNiFiUeq6tafXJumU6izOJon1EvEMZ';

// ─── Web Push (VAPID) ───────────────────────────────────────
webpush.setVapidDetails(
  'mailto:admin@somekorean.com',
  'BLVT7DZrnaD96Ygh4FlIaUjcexV0xFOkKs91apzUUxZQxzO5zS06oIW18AVj8vnKuzH_Kev3zYGGL1g7pdsC438',
  'AwUSoTwUg91rv_Ew0dRSH9hAhJn0MqXXA9xrj_eWCyg'
);

// ─── MySQL Pool ─────────────────────────────────────────────
const db = mysql.createPool({
  host: '127.0.0.1',
  user: 'somekorean_user',
  password: 'SK_DB@2026!secure',
  database: 'somekorean',
  waitForConnections: true,
  connectionLimit: 5,
});

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

  socket.on('elder:sos', async (data) => {
    console.log(`SOS from user ${userId}!`);
    if (data.guardianUserId) {
      const sent = sendToUser(data.guardianUserId, 'elder:sos-alert', {
        elderId: userId,
        elderName: data.elderName,
        lat: data.lat,
        lng: data.lng,
        time: new Date().toISOString()
      });
      // 보호자가 오프라인이면 푸시 알림 발송
      if (!sent) {
        await sendPushToUser(data.guardianUserId, {
          title: '\uD83D\uDEA8 긴급 SOS',
          body: (data.elderName || '어르신') + '님이 SOS를 발동했습니다!',
          icon: '/icons/icon-192x192.png',
          url: '/elder/guardian'
        });
      }
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
  socket.on('webrtc:call-request', (data) => {
    sendToUser(data.targetUserId, 'webrtc:call-request', {
      from: userId, callerName: data.callerName, callType: data.callType
    });
  });

  socket.on('webrtc:reject', (data) => {
    sendToUser(data.targetUserId, 'webrtc:reject', { from: userId });
  });

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
  if (sockets && sockets.size > 0) {
    sockets.forEach(sid => io.to(sid).emit(event, data));
    return true;
  }
  return false;
}

// ─── 푸시 알림 발송 함수 ─────────────────────────
async function sendPushToUser(userId, payload) {
  try {
    const [rows] = await db.query(
      'SELECT id, endpoint, p256dh, auth FROM push_subscriptions WHERE user_id = ?',
      [String(userId)]
    );
    if (!rows.length) {
      console.log(`No push subscriptions for user ${userId}`);
      return false;
    }
    const pushPayload = JSON.stringify(payload);
    let sent = false;
    for (const row of rows) {
      const subscription = {
        endpoint: row.endpoint,
        keys: { p256dh: row.p256dh, auth: row.auth }
      };
      try {
        await webpush.sendNotification(subscription, pushPayload);
        sent = true;
        console.log(`Push sent to user ${userId} (sub ${row.id})`);
      } catch (err) {
        console.error(`Push failed for sub ${row.id}:`, err.statusCode, err.body);
        if (err.statusCode === 410 || err.statusCode === 404) {
          await db.query('DELETE FROM push_subscriptions WHERE id = ?', [row.id]);
          console.log(`Deleted expired subscription ${row.id}`);
        }
      }
    }
    return sent;
  } catch (err) {
    console.error('sendPushToUser error:', err);
    return false;
  }
}

// Laravel에서 호출할 수 있는 REST API
app.use(express.json());

// ─── 푸시 구독 저장 API ────────────────────────────
app.post('/push-subscribe', async (req, res) => {
  try {
    const { userId, subscription } = req.body;
    if (!userId || !subscription || !subscription.endpoint) {
      return res.status(400).json({ error: 'userId and subscription required' });
    }
    const { endpoint, keys } = subscription;
    const p256dh = keys?.p256dh || '';
    const auth = keys?.auth || '';

    // Upsert: delete old same-endpoint, insert new
    await db.query('DELETE FROM push_subscriptions WHERE user_id = ? AND endpoint = ?', [String(userId), endpoint]);
    await db.query(
      'INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, created_at, updated_at) VALUES (?, ?, ?, ?, NOW(), NOW())',
      [String(userId), endpoint, p256dh, auth]
    );
    console.log(`Push subscription saved for user ${userId}`);
    res.json({ success: true });
  } catch (err) {
    console.error('push-subscribe error:', err);
    res.status(500).json({ error: 'Failed to save subscription' });
  }
});

app.post('/send-notification', async (req, res) => {
  const { userId, event, data } = req.body;
  const socketSent = sendToUser(String(userId), event || 'notification', data || {});
  if (!socketSent) {
    // 오프라인이면 PWA 푸시로
    await sendPushToUser(userId, {
      title: (data && data.title) || 'SomeKorean',
      body: (data && (data.message || data.body)) || '새 알림',
      icon: '/icons/icon-192x192.png',
      url: (data && data.url) || '/elder'
    });
  }
  res.json({ sent: true, method: socketSent ? 'socket' : 'push' });
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
