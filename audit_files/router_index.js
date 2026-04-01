import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
    // 홈
    { path: '/', component: () => import('../pages/Home.vue'), name: 'home' },

    // 인증
    { path: '/auth/register', component: () => import('../pages/auth/Register.vue'), name: 'register', meta: { guest: true } },
    { path: '/auth/login',    component: () => import('../pages/auth/Login.vue'),    name: 'login',    meta: { guest: true } },

    // 커뮤니티
    { path: '/community',           component: () => import('../pages/community/BoardList.vue'),  name: 'boards' },
    { path: '/community/write',     component: () => import('../pages/community/PostWrite.vue'),  name: 'post-write',  meta: { auth: true } },
    { path: '/community/post/:id',  component: () => import('../pages/community/PostDetail.vue'), name: 'post-detail' },
    { path: '/community/:slug',     component: () => import('../pages/community/PostList.vue'),   name: 'post-list' },

    // 동호회
    { path: '/clubs', component: () => import('../pages/community/ClubList.vue'), name: 'clubs' },
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
    { path: '/events',          component: () => import('../pages/events/EventList.vue'),   name: 'events' },
    { path: '/events/create',   component: () => import('../pages/events/EventCreate.vue'), name: 'event-create', meta: { auth: true } },
    { path: '/events/:id(\\d+)', component: () => import('../pages/events/EventDetail.vue'), name: 'event-detail' },

    // 알바 라이드
    { path: '/ride',                  component: () => import('../pages/ride/RideMain.vue'),       name: 'ride' },
    { path: '/ride/request',          component: () => import('../pages/ride/RideRequest.vue'),    name: 'ride-request',  meta: { auth: true } },
    { path: '/ride/history',          component: () => import('../pages/ride/RideHistory.vue'),    name: 'ride-history',  meta: { auth: true } },
    { path: '/ride/driver',           component: () => import('../pages/ride/DriverDashboard.vue'),name: 'driver',        meta: { auth: true } },
    { path: '/ride/driver/register',  component: () => import('../pages/ride/DriverRegister.vue'), name: 'driver-register', meta: { auth: true } },

    // 매칭
    { path: '/match',          component: () => import('../pages/match/MatchHome.vue'),         name: 'match',         meta: { auth: true } },
    { path: '/match/profile',  component: () => import('../pages/match/MatchProfileSetup.vue'), name: 'match-profile', meta: { auth: true } },
    { path: '/match/browse',   component: () => import('../pages/match/MatchBrowse.vue'),       name: 'match-browse',  meta: { auth: true } },

    // 게임/퀴즈
    { path: '/games',           component: () => import('../pages/games/GameLobby.vue'),   name: 'games' },
    { path: '/games/quiz',      component: () => import('../pages/games/QuizGame.vue'),    name: 'quiz',        meta: { auth: true } },
    { path: '/games/go-stop',   component: () => import('../pages/games/GoStop.vue'),      name: 'go-stop',     meta: { auth: true } },
    { path: '/games/go-stop/solo', component: () => import('../pages/games/GoStopSolo.vue'),  name: 'go-stop-solo' },
    { path: '/games/blackjack',    component: () => import('../pages/games/Blackjack.vue'),    name: 'blackjack' },
    { path: '/games/leaderboard',component: () => import('../pages/games/Leaderboard.vue'),name: 'leaderboard' },
    { path: '/games/shop',      component: () => import('../pages/games/PointShop.vue'),   name: 'point-shop',  meta: { auth: true } },

    // 관리자 (중첩 라우트)
    {
        path: '/admin',
        component: () => import('../pages/admin/AdminLayout.vue'),
        meta: { auth: true, admin: true },
        children: [
            { path: '',        redirect: '/admin/overview' },
            { path: 'overview', component: () => import('../pages/admin/Overview.vue'),  name: 'admin-overview' },
            { path: 'users',    component: () => import('../pages/admin/Users.vue'),     name: 'admin-users' },
            { path: 'content',  component: () => import('../pages/admin/Content.vue'),   name: 'admin-content' },
            { path: 'elder',    component: () => import('../pages/admin/Elder.vue'),      name: 'admin-elder' },
            { path: 'business', component: () => import('../pages/admin/Business.vue'),  name: 'admin-business' },
            { path: 'rides',    component: () => import('../pages/admin/Rides.vue'),     name: 'admin-rides' },
            { path: 'groupbuy', component: () => import('../pages/admin/GroupBuy.vue'),  name: 'admin-groupbuy' },
            { path: 'chats',    component: () => import('../pages/admin/Chats.vue'),     name: 'admin-chats' },
            { path: 'system',   component: () => import('../pages/admin/System.vue'),    name: 'admin-system' },
            { path: 'members',  component: () => import('../pages/admin/Members.vue'),   name: 'admin-members' },
            { path: 'payments', component: () => import('../pages/admin/Payments.vue'), name: 'admin-payments' },
            { path: 'banners',  component: () => import('../pages/admin/Banners.vue'),  name: 'admin-banners' },
            { path: 'menus',    component: () => import('../pages/admin/MenuManager.vue'), name: 'admin-menus' },
            { path: 'boards',   component: () => import('../pages/admin/BoardManager.vue'), name: 'admin-boards' },
            { path: 'site',     component: () => import('../pages/admin/SiteSettings.vue'), name: 'admin-site' },
            { path: 'friends',         component: () => import('../pages/admin/AdminFriends.vue'),   name: 'admin-friends' },
            { path: 'matching',        component: () => import('../pages/admin/AdminMatching.vue'),  name: 'admin-matching' },
            { path: 'clubs',           component: () => import('../pages/admin/AdminClubs.vue'),     name: 'admin-clubs' },
            { path: 'events-admin',    component: () => import('../pages/admin/AdminEvents.vue'),    name: 'admin-events' },
            { path: 'jobs',            component: () => import('../pages/admin/AdminJobs.vue'),      name: 'admin-jobs' },
            { path: 'market',          component: () => import('../pages/admin/AdminMarket.vue'),    name: 'admin-market' },
            { path: 'realestate-admin', component: () => import('../pages/admin/AdminRealestate.vue'), name: 'admin-realestate' },
            { path: 'mentor-admin',    component: () => import('../pages/admin/AdminMentor.vue'),    name: 'admin-mentor' },
            { path: 'news-admin',      component: () => import('../pages/admin/AdminNews.vue'),      name: 'admin-news' },
            { path: 'shorts-admin',    component: () => import('../pages/admin/AdminShorts.vue'),    name: 'admin-shorts' },
            { path: 'shopping-admin',  component: () => import('../pages/admin/AdminShopping.vue'),  name: 'admin-shopping' },
            { path: 'ai-admin',        component: () => import('../pages/admin/AdminAI.vue'),        name: 'admin-ai' },
            { path: 'games-admin',     component: () => import('../pages/admin/AdminGames.vue'),     name: 'admin-games' },
            { path: 'qa-admin',        component: () => import('../pages/admin/AdminQa.vue'),         name: 'admin-qa' },
            { path: 'recipes-admin',   component: () => import('../pages/admin/AdminRecipes.vue'),    name: 'admin-recipes' },
            { path: 'wallet', component: () => import('../pages/admin/AdminWallet.vue'), name: 'admin-wallet' },
        ],
    },

    // 포커
    { path: '/games/poker',         component: () => import('../pages/games/Poker.vue'),        name: 'poker',         meta: { auth: true } },
    { path: '/games/holdem',        component: () => import('../pages/games/HoldemSolo.vue'),   name: 'holdem' },
    { path: '/games/memory',        component: () => import('../pages/games/MemoryGame.vue'),   name: 'memory' },
    { path: '/games/2048',          component: () => import('../pages/games/Game2048.vue'),     name: 'game2048' },
    { path: '/games/tower-defense', component: () => import('../pages/games/GameTowerDefense.vue'), name: 'game-tower-defense' },
  { path: '/games/stroop', component: () => import('../pages/games/GameStroop.vue'), name: 'game-stroop' },
  { path: '/games/breathing', component: () => import('../pages/games/GameBreathing.vue'), name: 'game-breathing' },
  { path: '/games/senior-memory', component: () => import('../pages/games/GameSeniorMemory.vue'), name: 'game-senior-memory' },
  { path: '/games/senior-bingo', component: () => import('../pages/games/GameBingo.vue'), name: 'game-senior-bingo' },
  { path: '/games/brain-calc', component: () => import('../pages/games/GameSpeedCalc.vue'), name: 'game-brain-calc' },
  { path: '/games/picture-memory', component: () => import('../pages/games/GameMemory.vue'), name: 'game-picture-memory' },
  { path: '/games/bingo',         component: () => import('../pages/games/BingoGame.vue'),    name: 'bingo' },

    { path: '/games/car-jump', component: () => import('../pages/games/GameCarJump.vue'), name: 'game-carjump' },
    { path: '/games/number-memory', component: () => import('../pages/games/GameNumberMemory.vue'), name: 'game-numbermem' },
    { path: '/games/tower-defense', component: () => import('../pages/games/GameTowerDefense.vue'), name: 'game-tower-defense' },
  { path: '/games/stroop', component: () => import('../pages/games/GameStroop.vue'), name: 'game-stroop' },
  { path: '/games/breathing', component: () => import('../pages/games/GameBreathing.vue'), name: 'game-breathing' },
  { path: '/games/senior-memory', component: () => import('../pages/games/GameSeniorMemory.vue'), name: 'game-senior-memory' },
  { path: '/games/senior-bingo', component: () => import('../pages/games/GameBingo.vue'), name: 'game-senior-bingo' },
  { path: '/games/brain-calc', component: () => import('../pages/games/GameSpeedCalc.vue'), name: 'game-brain-calc' },
  { path: '/games/picture-memory', component: () => import('../pages/games/GameMemory.vue'), name: 'game-picture-memory' },
  { path: '/games/bingo', component: () => import('../pages/games/GameBingo.vue'), name: 'game-bingo' },
  { path: '/games/memory', component: () => import('../pages/games/GameMemory.vue'), name: 'game-memory' },
  { path: '/games/us-life', component: () => import('../pages/games/GameUSLife.vue'), name: 'game-us-life' },
  { path: '/games/proverb', component: () => import('../pages/games/GameProverb.vue'), name: 'game-proverb' },
  { path: '/games/hanja', component: () => import('../pages/games/GameHanja.vue'), name: 'game-hanja' },
  { path: '/games/health', component: () => import('../pages/games/GameHealth.vue'), name: 'game-health' },
  { path: '/games/spelling', component: () => import('../pages/games/GameSpelling.vue'), name: 'game-spelling' },
  { path: '/games/speed-calc', component: () => import('../pages/games/GameSpeedCalc.vue'), name: 'game-speed-calc' },
  { path: '/games/coding-quiz', component: () => import('../pages/games/GameCodingQuiz.vue'), name: 'game-coding-quiz' },
  { path: '/games/history', component: () => import('../pages/games/GameHistory.vue'), name: 'game-history' },
  { path: '/games/stock', component: () => import('../pages/games/GameStockSim.vue'), name: 'game-stock' },
  { path: '/games/sat-words', component: () => import('../pages/games/GameSATWords.vue'), name: 'game-sat-words' },
  { path: '/games/math-challenge', component: () => import('../pages/games/GameMathChallenge.vue'), name: 'game-math-challenge' },
  { path: '/games/world-geo', component: () => import('../pages/games/GameWorldGeo.vue'), name: 'game-world-geo' },
  { path: '/games/maze', component: () => import('../pages/games/GameMaze.vue'), name: 'game-maze' },
  { path: '/games/puzzle', component: () => import('../pages/games/GamePuzzle.vue'), name: 'game-puzzle' },
  { path: '/games/engcard', component: () => import('../pages/games/GameEngCard.vue'), name: 'game-engcard' },
  { path: '/games/wordchain', component: () => import('../pages/games/GameWordChain.vue'), name: 'game-wordchain' },
  { path: '/games/typing', component: () => import('../pages/games/GameTyping.vue'), name: 'game-typing' },
  { path: '/games/multiplication', component: () => import('../pages/games/GameMultiplication.vue'), name: 'game-multiplication' },
  { path: '/games/wordblank', component: () => import('../pages/games/GameWordBlank.vue'), name: 'game-wordblank' },
  { path: '/games/wordle', component: () => import('../pages/games/GameWordle.vue'), name: 'game-wordle' },
    { path: '/games/hangul', component: () => import('../pages/games/GameHangul.vue'), name: 'game-hangul' },
    { path: '/games/alphabet', component: () => import('../pages/games/GameAlphabet.vue'), name: 'game-alphabet' },
    { path: '/games/counting', component: () => import('../pages/games/GameCounting.vue'), name: 'game-counting' },
        { path: '/games/colors', component: () => import('../pages/games/GameColors.vue'), name: 'game-colors' },
    { path: '/games/animals', component: () => import('../pages/games/GameAnimals.vue'), name: 'game-animals' },
    { path: '/games/shapes', component: () => import('../pages/games/GameShapes.vue'), name: 'game-shapes' },
        { path: '/games/wordcard', component: () => import('../pages/games/GameWordCard.vue'), name: 'game-wordcard' },
    { path: '/games/math-basic', component: () => import('../pages/games/GameMathBasic.vue'), name: 'game-math-basic' },
  { path: '/games/colors', component: () => import('../pages/games/GameColors.vue'), name: 'game-colors' },
    { path: '/games/omok',          component: () => import('../pages/games/OmokGame.vue'),     name: 'omok' },

    // 알림
    { path: '/notifications',    component: () => import('../pages/Notifications.vue'),        name: 'notifications', meta: { auth: true } },

    // 뉴스
    { path: '/news',             component: () => import('../pages/news/NewsList.vue'),        name: 'news' },
    { path: '/news/:id',         component: () => import('../pages/news/NewsDetail.vue'),      name: 'news-detail' },

    // Q&A
    { path: '/qa',               component: () => import('../pages/qa/QaList.vue'),            name: 'qa' },
    { path: '/qa/:id(\\d+)',     component: () => import('../pages/qa/QaDetail.vue'),          name: 'qa-detail' },

    // 레시피
    { path: '/recipes',          component: () => import('../pages/recipes/RecipeList.vue'),   name: 'recipes' },
    { path: '/recipes/create', component: () => import('../pages/recipes/RecipeCreate.vue'), name: 'recipe-create', meta: { requiresAuth: true } },
    { path: '/recipes/:id(\\d+)', component: () => import('../pages/recipes/RecipeDetail.vue'), name: 'recipe-detail' },

    // 검색
    { path: '/search',           component: () => import('../pages/Search.vue'),               name: 'search' },

    // 프로필 수정 & 대쉬보드
    { path: '/profile/edit',     component: () => import('../pages/profile/ProfileEdit.vue'),  name: 'profile-edit', meta: { auth: true } },
    { path: '/dashboard',        component: () => import('../pages/profile/UserDashboard.vue'), name: 'dashboard',   meta: { auth: true } },

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
    { path: '/ai',        component: () => import('../pages/ai/AISearch.vue'),         name: 'ai-search' },
    { path: '/groupbuy',  component: () => import('../pages/groupbuy/GroupBuyHome.vue'), name: 'groupbuy' },
    { path: '/mentor',    component: () => import('../pages/mentor/MentorHome.vue'),    name: 'mentor' },

  { path: '/claim-business/:id', component: () => import('../pages/ClaimBusiness.vue'), meta: { title: '소유권 신청' } },
  { path: '/my-business', component: () => import('../pages/OwnerDashboard.vue'), meta: { requiresAuth: true, title: '내 업소 관리' } },
  { path: '/premium', component: () => import('../pages/PremiumUpgrade.vue'), meta: { title: '프리미엄 업그레이드' } },
  { path: '/verify-business/:token', component: () => import('../pages/EmailVerifyBusiness.vue'), meta: { title: '이메일 인증' } },

    // 404
    { path: '/:pathMatch(.*)*', component: () => import('../pages/NotFound.vue'), name: 'not-found' },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
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