import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
    // 홈
    { path: '/', component: () => import('../pages/Home.vue'), name: 'home' },

    // 인증
    { path: '/auth/register', component: () => import('../pages/auth/Register.vue'), name: 'register', meta: { guest: true } },
    { path: '/auth/login',    component: () => import('../pages/auth/Login.vue'),    name: 'login',    meta: { guest: true } },

    // 커뮤니티 v2
    { path: '/community',            component: () => import('../pages/community/CommunityHome.vue'),     name: 'community-home' },
    { path: '/community/write',      component: () => import('../pages/community/CommunityWrite.vue'),    name: 'community-write', meta: { auth: true } },
    { path: '/community/:slug',      component: () => import('../pages/community/CommunityCategory.vue'), name: 'community-category' },
    { path: '/community/:slug/:id',  component: () => import('../pages/community/CommunityPost.vue'),     name: 'community-post' },
    { path: '/community/:slug/:id/edit', component: () => import('../pages/community/CommunityWrite.vue'), name: 'community-edit', meta: { auth: true } },

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
    { path: '/directory/:id/claim', component: () => import('../pages/ClaimBusiness.vue'),              name: 'claim-business', meta: { auth: true } },
    { path: '/email-verify-business/:token', component: () => import('../pages/EmailVerifyBusiness.vue'), name: 'email-verify-business' },

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
    { path: '/games/go-stop/solo', component: () => import('../pages/games/GoStopSolo.vue'),  name: 'go-stop-solo' },
    { path: '/games/shop',      component: () => import('../pages/games/PointShop.vue'),   name: 'point-shop',  meta: { auth: true } },

    // 관리자
    // 어드민 (중첩 라우트)
    // Q&A
  { path: '/qa', component: () => import('../pages/qa/QAHome.vue'), name: 'qa-home' },
  { path: '/qa/write', component: () => import('../pages/qa/QAWrite.vue'), name: 'qa-write', meta: { auth: true } },
  { path: '/qa/:slug', component: () => import('../pages/qa/QACategory.vue'), name: 'qa-category' },
  { path: '/qa/:slug/:id', component: () => import('../pages/qa/QAQuestion.vue'), name: 'qa-question' },
  { path: '/user/:userId/resolved', component: () => import('../pages/qa/UserResolved.vue'), name: 'user-resolved' },

    // 레시피
    { path: '/recipes',         component: () => import('../pages/recipes/RecipeList.vue'),   name: 'recipes' },
    { path: '/recipes/create',  component: () => import('../pages/recipes/RecipeCreate.vue'), name: 'recipe-create', meta: { auth: true } },
    { path: '/recipes/:id',     component: () => import('../pages/recipes/RecipeDetail.vue'), name: 'recipe-detail' },

    // 공동구매
    { path: '/groupbuy', component: () => import('../pages/groupbuy/GroupBuyHome.vue'), name: 'groupbuy' },

    // 멘토링
    { path: '/mentor', component: () => import('../pages/mentor/MentorHome.vue'), name: 'mentor' },

    // AI 검색
    { path: '/ai', component: () => import('../pages/ai/AISearch.vue'), name: 'ai-search' },


    {
        path: '/admin',
        component: () => import('../pages/admin/AdminLayout.vue'),
        meta: { auth: true, admin: true },
        children: [
            { path: '', redirect: '/admin/overview' },
            { path: 'overview', name: 'admin', component: () => import('../pages/admin/Overview.vue') },
            { path: 'members', name: 'admin-members', component: () => import('../pages/admin/Users.vue') },
            { path: 'content', name: 'admin-content', component: () => import('../pages/admin/Content.vue') },
            { path: 'matching', name: 'admin-matching', component: () => import('../pages/admin/AdminMatching.vue') },
            { path: 'friends', name: 'admin-friends', component: () => import('../pages/admin/AdminFriends.vue') },
            { path: 'boards', name: 'admin-boards', component: () => import('../pages/admin/BoardManager.vue') },
            { path: 'clubs', name: 'admin-clubs', component: () => import('../pages/admin/AdminClubs.vue') },
            { path: 'events-admin', name: 'admin-events', component: () => import('../pages/admin/AdminEvents.vue') },
            { path: 'chats', name: 'admin-chats', component: () => import('../pages/admin/Chats.vue') },
            { path: 'news-admin', name: 'admin-news', component: () => import('../pages/admin/AdminNews.vue') },
            { path: 'qa-admin', name: 'admin-qa', component: () => import('../pages/admin/AdminQa.vue') },
            { path: 'recipes-admin', name: 'admin-recipes', component: () => import('../pages/admin/AdminRecipes.vue') },
            { path: 'shorts-admin', name: 'admin-shorts', component: () => import('../pages/admin/AdminShorts.vue') },
            { path: 'music-admin', name: 'admin-music', component: () => import('../pages/admin/AdminMusic.vue') },
            { path: 'shopping-admin', name: 'admin-shopping', component: () => import('../pages/admin/AdminShopping.vue') },
            { path: 'jobs', name: 'admin-jobs', component: () => import('../pages/admin/AdminJobs.vue') },
            { path: 'realestate-admin', name: 'admin-realestate', component: () => import('../pages/admin/AdminRealestate.vue') },
            { path: 'business', name: 'admin-business', component: () => import('../pages/admin/Business.vue') },
            { path: 'rides', name: 'admin-rides', component: () => import('../pages/admin/Rides.vue') },
            { path: 'groupbuy', name: 'admin-groupbuy', component: () => import('../pages/admin/GroupBuy.vue') },
            { path: 'elder', name: 'admin-elder', component: () => import('../pages/admin/Elder.vue') },
            { path: 'mentor-admin', name: 'admin-mentor', component: () => import('../pages/admin/AdminMentor.vue') },
            { path: 'games-admin', name: 'admin-games', component: () => import('../pages/admin/AdminGames.vue') },
            { path: 'payments', name: 'admin-payments', component: () => import('../pages/admin/AdminWallet.vue') },
            { path: 'system', name: 'admin-system', component: () => import('../pages/admin/System.vue') },
            { path: 'menus', redirect: '/admin/site' },
            { path: 'site', name: 'admin-site', component: () => import('../pages/admin/SiteSettings.vue') },
            { path: 'ai', name: 'admin-ai', component: () => import('../pages/admin/AdminAI.vue') },
            { path: 'market', name: 'admin-market', component: () => import('../pages/admin/AdminMarket.vue') },
            { path: 'banners', name: 'admin-banners', component: () => import('../pages/admin/Banners.vue') },
            { path: 'members-list', name: 'admin-members-list', component: () => import('../pages/admin/Members.vue') },
            { path: 'wallet-payments', name: 'admin-wallet-payments', component: () => import('../pages/admin/Payments.vue') },
            { path: 'security', name: 'admin-security', component: () => import('../pages/admin/AdminSecurity.vue') },
        ]
    },

    // 포커
    { path: '/games/poker',         component: () => import('../pages/games/Poker.vue'),        name: 'poker',         meta: { auth: true } },
  { path: '/games/alphabet', name: 'game-alphabet', component: () => import('../pages/games/GameAlphabet.vue') },
  { path: '/games/counting', name: 'game-counting', component: () => import('../pages/games/GameCounting.vue') },
  { path: '/games/colors', name: 'game-colors', component: () => import('../pages/games/GameColors.vue') },
  { path: '/games/animals', name: 'game-animals', component: () => import('../pages/games/GameAnimals.vue') },
  { path: '/games/shapes', name: 'game-shapes', component: () => import('../pages/games/GameShapes.vue') },
  { path: '/games/wordcard', name: 'game-wordcard', component: () => import('../pages/games/GameWordCard.vue') },
  { path: '/games/math-basic', name: 'game-math-basic', component: () => import('../pages/games/GameMathBasic.vue') },
  { path: '/games/hangul', name: 'game-hangul', component: () => import('../pages/games/GameHangul.vue') },
  { path: '/games/engcard', name: 'game-engcard', component: () => import('../pages/games/GameEngCard.vue') },
  { path: '/games/math-challenge', name: 'game-math-challenge', component: () => import('../pages/games/GameMathChallenge.vue') },
  { path: '/games/puzzle', name: 'game-puzzle', component: () => import('../pages/games/GamePuzzle.vue') },
  { path: '/games/maze', name: 'game-maze', component: () => import('../pages/games/GameMaze.vue') },
  { path: '/games/multiplication', name: 'game-multiplication', component: () => import('../pages/games/GameMultiplication.vue') },
  { path: '/games/typing', name: 'game-typing', component: () => import('../pages/games/GameTyping.vue') },
  { path: '/games/car-jump', name: 'game-carjump', component: () => import('../pages/games/GameCarJump.vue') },
  { path: '/games/wordchain', name: 'game-wordchain', component: () => import('../pages/games/GameWordChain.vue') },
  { path: '/games/wordblank', name: 'game-wordblank', component: () => import('../pages/games/GameWordBlank.vue') },
  { path: '/games/speed-calc', name: 'game-speed-calc', component: () => import('../pages/games/GameSpeedCalc.vue') },
  { path: '/games/coding-quiz', name: 'game-coding-quiz', component: () => import('../pages/games/GameCodingQuiz.vue') },
  { path: '/games/tower-defense', name: 'game-tower-defense', component: () => import('../pages/games/GameTowerDefense.vue') },
  { path: '/games/spelling', name: 'game-spelling', component: () => import('../pages/games/GameSpelling.vue') },
  { path: '/games/world-geo', name: 'game-world-geo', component: () => import('../pages/games/GameWorldGeo.vue') },
  { path: '/games/sat-words', name: 'game-sat-words', component: () => import('../pages/games/GameSATWords.vue') },
  { path: '/games/stock', name: 'game-stock', component: () => import('../pages/games/GameStockSim.vue') },
  { path: '/games/matgo', name: 'game-matgo', component: () => import('../pages/games/GoStop.vue') },
  { path: '/games/us-life', name: 'game-us-life', component: () => import('../pages/games/GameUSLife.vue') },
  { path: '/games/blackjack', name: 'game-blackjack', component: () => import('../pages/games/Blackjack.vue') },
  { path: '/games/wordle', name: 'game-wordle', component: () => import('../pages/games/GameWordle.vue') },
  { path: '/games/memory', name: 'game-memory', component: () => import('../pages/games/MemoryGame.vue') },
  { path: '/games/2048', name: 'game-2048', component: () => import('../pages/games/Game2048.vue') },
  { path: '/games/omok', name: 'game-omok', component: () => import('../pages/games/OmokGame.vue') },
  { path: '/games/holdem', name: 'game-holdem', component: () => import('../pages/games/HoldemSolo.vue') },
  { path: '/games/go-stop', name: 'game-gostop', component: () => import('../pages/games/GoStop.vue') },
  { path: '/games/bingo', name: 'game-bingo', component: () => import('../pages/games/BingoGame.vue') },
  { path: '/games/brain-calc', name: 'game-brain-calc', component: () => import('../pages/games/GameSpeedCalc.vue') },
  { path: '/games/senior-bingo', name: 'game-senior-bingo', component: () => import('../pages/games/GameBingo.vue') },
  { path: '/games/senior-memory', name: 'game-senior-memory', component: () => import('../pages/games/GameSeniorMemory.vue') },
  { path: '/games/breathing', name: 'game-breathing', component: () => import('../pages/games/GameBreathing.vue') },
  { path: '/games/word-search', name: 'game-word-search', component: () => import('../pages/games/GameWordBlank.vue') },
  { path: '/games/stroop', name: 'game-stroop', component: () => import('../pages/games/GameStroop.vue') },
  { path: '/games/proverb', name: 'game-proverb', component: () => import('../pages/games/GameProverb.vue') },
  { path: '/games/picture-memory', name: 'game-picture-memory', component: () => import('../pages/games/GameSeniorMemory.vue') },
  { path: '/games/number-memory', name: 'game-number-memory', component: () => import('../pages/games/GameNumberMemory.vue') },
  { path: '/games/snake', name: 'game-snake', component: () => import('../pages/games/GameSnake.vue') },
  { path: '/games/pacman', name: 'game-pacman', component: () => import('../pages/games/GamePacman.vue') },
  { path: '/games/flappy', name: 'game-flappy', component: () => import('../pages/games/GameFlappy.vue') },
  { path: '/games/duckhunt', name: 'game-duckhunt', component: () => import('../pages/games/GameDuckHunt.vue') },
  { path: '/games/slots', name: 'game-slots', component: () => import('../pages/games/GameSlots.vue') },
  { path: '/games/hextris', name: 'game-hextris', component: () => import('../pages/games/GameHextris.vue') },
  { path: '/games/mahjong', name: 'game-mahjong', component: () => import('../pages/games/GameMahjong.vue') },
  { path: '/games/hanja', name: 'game-hanja', component: () => import('../pages/games/GameHanja.vue') },
  { path: '/games/health', name: 'game-health', component: () => import('../pages/games/GameHealth.vue') },
  { path: '/games/history', name: 'game-history', component: () => import('../pages/games/GameHistory.vue') },
  { path: '/games/leaderboard', name: 'game-leaderboard', component: () => import('../pages/games/Leaderboard.vue') },

    // 알림
    { path: '/notifications',    component: () => import('../pages/Notifications.vue'),        name: 'notifications', meta: { auth: true } },

    // 뉴스
    { path: '/news',             component: () => import('../pages/news/NewsList.vue'),        name: 'news' },
    { path: '/news/:id',         component: () => import('../pages/news/NewsDetail.vue'),      name: 'news-detail' },

    // 검색
    { path: '/search',           component: () => import('../pages/Search.vue'),               name: 'search' },

    // 프로필 수정 & 대쉬보드
    { path: '/profile/edit',     component: () => import('../pages/profile/ProfileEdit.vue'),  name: 'profile-edit', meta: { auth: true } },
    { path: '/dashboard',        component: () => import('../pages/profile/UserDashboard.vue'), name: 'dashboard',   meta: { auth: true } },

    // 친구
    { path: '/friends', component: () => import('../pages/friends/FriendList.vue'), name: 'friends', meta: { auth: true } },

    // 음악듣기
    { path: '/music', component: () => import('../pages/music/MusicHome.vue'), name: 'music' },

    // 숏츠
    { path: '/shorts',        component: () => import('../pages/shorts/ShortsHome.vue'),   name: 'shorts' },
    { path: '/shorts/upload', component: () => import('../pages/shorts/ShortsUpload.vue'), name: 'shorts-upload', meta: { auth: true } },

    // 쇼핑정보
    { path: '/shopping', component: () => import('../pages/shopping/ShoppingHome.vue'), name: 'shopping' },

    // 업소 오너 대시보드
    { path: '/owner-dashboard', component: () => import('../pages/OwnerDashboard.vue'), name: 'owner-dashboard', meta: { auth: true } },

    // 프리미엄 업그레이드
    { path: '/premium-upgrade', component: () => import('../pages/PremiumUpgrade.vue'), name: 'premium-upgrade' },

    // 코인 규칙
    { path: '/rules', component: () => import('../pages/PointRules.vue'), name: 'rules' },

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

    // initPromise가 resolve될 때까지 대기 (fetchMe 완료 보장)
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