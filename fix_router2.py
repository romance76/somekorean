import paramiko, sys

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=20)
sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-600:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-300:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

router_js = r"""import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
    // 홈
    { path: '/', component: () => import('../pages/Home.vue'), name: 'home' },

    // 인증
    { path: '/auth/register', component: () => import('../pages/auth/Register.vue'), name: 'register', meta: { guest: true } },
    { path: '/auth/login',    component: () => import('../pages/auth/Login.vue'),    name: 'login',    meta: { guest: true } },

    // 커뮤니티
    { path: '/community',           component: () => import('../pages/community/BoardList.vue'),  name: 'boards' },
    { path: '/community/qna',       component: () => import('../pages/community/QnAHome.vue'),    name: 'qna' },
    { path: '/community/write',     component: () => import('../pages/community/PostWrite.vue'),  name: 'post-write',  meta: { auth: true } },
    { path: '/community/post/:id',  component: () => import('../pages/community/PostDetail.vue'), name: 'post-detail' },
    { path: '/community/:slug',     component: () => import('../pages/community/PostList.vue'),   name: 'post-list' },

    // 동호회
    { path: '/clubs',     component: () => import('../pages/community/ClubList.vue'),   name: 'clubs' },
    { path: '/clubs/:id', component: () => import('../pages/community/ClubDetail.vue'), name: 'club-detail' },

    // 구인구직
    { path: '/jobs',        component: () => import('../pages/jobs/JobList.vue'),   name: 'jobs' },
    { path: '/jobs/write',  component: () => import('../pages/jobs/JobWrite.vue'),  name: 'job-write', meta: { auth: true } },
    { path: '/jobs/:id',    component: () => import('../pages/jobs/JobDetail.vue'), name: 'job-detail' },

    // 중고장터
    { path: '/market',        component: () => import('../pages/market/MarketList.vue'),   name: 'market' },
    { path: '/market/write',  component: () => import('../pages/market/MarketWrite.vue'),  name: 'market-write', meta: { auth: true } },
    { path: '/market/:id',    component: () => import('../pages/market/MarketDetail.vue'), name: 'market-detail' },

    // 부동산
    { path: '/realestate',       component: () => import('../pages/realestate/RealEstateList.vue'),   name: 'realestate' },
    { path: '/realestate/write', component: () => import('../pages/realestate/RealEstateWrite.vue'),  name: 'realestate-write', meta: { auth: true } },
    { path: '/realestate/:id',   component: () => import('../pages/realestate/RealEstateDetail.vue'), name: 'realestate-detail' },

    // 업소록
    { path: '/directory',           component: () => import('../pages/directory/BusinessList.vue'),     name: 'directory' },
    { path: '/directory/register',  component: () => import('../pages/directory/BusinessRegister.vue'), name: 'business-register', meta: { auth: true } },
    { path: '/directory/:id',       component: () => import('../pages/directory/BusinessDetail.vue'),   name: 'business-detail' },

    // 포인트
    { path: '/points', component: () => import('../pages/points/PointDashboard.vue'), name: 'points', meta: { auth: true } },

    // 메시지
    { path: '/messages', component: () => import('../pages/messages/MessageInbox.vue'), name: 'messages', meta: { auth: true } },

    // 프로필
    { path: '/profile/:username', component: () => import('../pages/profile/UserProfile.vue'), name: 'profile' },

    // 채팅
    { path: '/chat',          component: () => import('../pages/chat/ChatRooms.vue'), name: 'chat-rooms', meta: { auth: true } },
    { path: '/chat/room/:id', component: () => import('../pages/chat/ChatRoom.vue'),  name: 'chat-room',  meta: { auth: true } },

    // 노인 안심
    { path: '/elder',          component: () => import('../pages/elder/ElderHome.vue'),         name: 'elder',          meta: { auth: true } },
    { path: '/elder/checkin',  component: () => import('../pages/elder/ElderCheckin.vue'),      name: 'elder-checkin',  meta: { auth: true } },
    { path: '/elder/guardian', component: () => import('../pages/elder/GuardianDashboard.vue'), name: 'elder-guardian', meta: { auth: true } },

    // 이벤트
    { path: '/events',           component: () => import('../pages/events/EventList.vue'),   name: 'events' },
    { path: '/events/create',    component: () => import('../pages/events/EventCreate.vue'), name: 'event-create', meta: { auth: true } },
    { path: '/events/:id(\\d+)', component: () => import('../pages/events/EventDetail.vue'), name: 'event-detail' },

    // 알바 라이드
    { path: '/ride',                 component: () => import('../pages/ride/RideMain.vue'),        name: 'ride' },
    { path: '/ride/request',         component: () => import('../pages/ride/RideRequest.vue'),     name: 'ride-request',    meta: { auth: true } },
    { path: '/ride/history',         component: () => import('../pages/ride/RideHistory.vue'),     name: 'ride-history',    meta: { auth: true } },
    { path: '/ride/driver',          component: () => import('../pages/ride/DriverDashboard.vue'), name: 'driver',          meta: { auth: true } },
    { path: '/ride/driver/register', component: () => import('../pages/ride/DriverRegister.vue'),  name: 'driver-register', meta: { auth: true } },

    // 매칭
    { path: '/match',         component: () => import('../pages/match/MatchHome.vue'),         name: 'match',         meta: { auth: true } },
    { path: '/match/profile', component: () => import('../pages/match/MatchProfileSetup.vue'), name: 'match-profile', meta: { auth: true } },
    { path: '/match/browse',  component: () => import('../pages/match/MatchBrowse.vue'),       name: 'match-browse',  meta: { auth: true } },

    // 게임/퀴즈
    { path: '/games',              component: () => import('../pages/games/GameLobby.vue'),   name: 'games' },
    { path: '/games/quiz',         component: () => import('../pages/games/QuizGame.vue'),    name: 'quiz',        meta: { auth: true } },
    { path: '/games/go-stop',      component: () => import('../pages/games/GoStop.vue'),      name: 'go-stop',     meta: { auth: true } },
    { path: '/games/go-stop/solo', component: () => import('../pages/games/GoStopSolo.vue'),  name: 'go-stop-solo' },
    { path: '/games/blackjack',    component: () => import('../pages/games/Blackjack.vue'),   name: 'blackjack' },
    { path: '/games/leaderboard',  component: () => import('../pages/games/Leaderboard.vue'), name: 'leaderboard' },
    { path: '/games/shop',         component: () => import('../pages/games/PointShop.vue'),   name: 'point-shop',  meta: { auth: true } },
    { path: '/games/poker',        component: () => import('../pages/games/Poker.vue'),        name: 'poker',       meta: { auth: true } },
    { path: '/games/holdem',       component: () => import('../pages/games/HoldemSolo.vue'),  name: 'holdem' },
    { path: '/games/memory',       component: () => import('../pages/games/MemoryGame.vue'),  name: 'memory' },
    { path: '/games/2048',         component: () => import('../pages/games/Game2048.vue'),    name: 'game2048' },
    { path: '/games/bingo',        component: () => import('../pages/games/BingoGame.vue'),   name: 'bingo' },
    { path: '/games/omok',         component: () => import('../pages/games/OmokGame.vue'),    name: 'omok' },

    // 관리자 (중첩 라우트)
    {
        path: '/admin',
        component: () => import('../pages/admin/AdminLayout.vue'),
        meta: { auth: true, admin: true },
        children: [
            { path: '',         redirect: '/admin/overview' },
            { path: 'overview', component: () => import('../pages/admin/Overview.vue'),  name: 'admin-overview' },
            { path: 'users',    component: () => import('../pages/admin/Users.vue'),     name: 'admin-users' },
            { path: 'content',  component: () => import('../pages/admin/Content.vue'),   name: 'admin-content' },
            { path: 'elder',    component: () => import('../pages/admin/Elder.vue'),      name: 'admin-elder' },
            { path: 'business', component: () => import('../pages/admin/Business.vue'),  name: 'admin-business' },
            { path: 'rides',    component: () => import('../pages/admin/Rides.vue'),     name: 'admin-rides' },
            { path: 'groupbuy', component: () => import('../pages/admin/GroupBuy.vue'),  name: 'admin-groupbuy' },
            { path: 'chats',    component: () => import('../pages/admin/Chats.vue'),     name: 'admin-chats' },
            { path: 'system',   component: () => import('../pages/admin/System.vue'),    name: 'admin-system' },
        ],
    },

    // 알림
    { path: '/notifications', component: () => import('../pages/Notifications.vue'), name: 'notifications', meta: { auth: true } },

    // 뉴스
    { path: '/news',     component: () => import('../pages/news/NewsList.vue'),   name: 'news' },
    { path: '/news/:id', component: () => import('../pages/news/NewsDetail.vue'), name: 'news-detail' },

    // 검색
    { path: '/search', component: () => import('../pages/Search.vue'), name: 'search' },

    // 프로필 수정 & 대쉬보드
    { path: '/profile/edit', component: () => import('../pages/profile/ProfileEdit.vue'),  name: 'profile-edit', meta: { auth: true } },
    { path: '/dashboard',    component: () => import('../pages/profile/UserDashboard.vue'), name: 'dashboard',   meta: { auth: true } },

    // 친구
    { path: '/friends', component: () => import('../pages/friends/FriendList.vue'), name: 'friends', meta: { auth: true } },

    // 숏츠
    { path: '/shorts',        component: () => import('../pages/shorts/ShortsHome.vue'),   name: 'shorts' },
    { path: '/shorts/upload', component: () => import('../pages/shorts/ShortsUpload.vue'), name: 'shorts-upload', meta: { auth: true } },

    // 쇼핑정보
    { path: '/shopping', component: () => import('../pages/shopping/ShoppingHome.vue'), name: 'shopping' },

    // 코인 규칙
    { path: '/rules', component: () => import('../pages/PointRules.vue'), name: 'rules' },

    // Phase 5 — AI / 공동구매 / 멘토링
    { path: '/ai',       component: () => import('../pages/ai/AISearch.vue'),          name: 'ai-search' },
    { path: '/groupbuy', component: () => import('../pages/groupbuy/GroupBuyHome.vue'), name: 'groupbuy' },
    { path: '/mentor',   component: () => import('../pages/mentor/MentorHome.vue'),    name: 'mentor' },

    // 404
    { path: '/:pathMatch(.*)*', component: () => import('../pages/NotFound.vue'), name: 'not-found' },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();

    // fetchMe 완료 대기 (is_admin 캐시 race condition 방지)
    await authStore.initPromise;

    if (to.meta.auth && !authStore.isLoggedIn) {
        return next({ name: 'login', query: { redirect: to.fullPath } });
    }
    if (to.meta.admin && !authStore.user?.is_admin) {
        return next({ name: 'home' });
    }
    if (to.meta.guest && authStore.isLoggedIn) {
        return next({ name: 'home' });
    }
    next();
});

export default router;
"""

with sftp.file(f'{APP}/resources/js/router/index.js', 'w') as f:
    f.write(router_js)
sys.stdout.buffer.write(b'router/index.js written\n')
sys.stdout.buffer.flush()

sftp.close()

run(f'cd {APP} && npm run build 2>&1 | tail -6', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -2')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

client.close()
sys.stdout.buffer.write(b'\n=== Done ===\n')
sys.stdout.buffer.flush()
