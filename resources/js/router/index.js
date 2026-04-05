import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Lazy-load helper
const p = (path) => () => import(`../pages/${path}.vue`)

const routes = [
  // ── Home ──
  { path: '/', name: 'home', component: p('Home') },

  // ── Auth ──
  { path: '/login', name: 'login', component: p('auth/Login'), meta: { guest: true } },
  { path: '/register', name: 'register', component: p('auth/Register'), meta: { guest: true } },

  // ── Community (Boards) ──
  { path: '/community', name: 'community', component: p('community/BoardList') },
  { path: '/community/write/:board?', name: 'community-write', component: p('community/PostWrite'), meta: { auth: true } },
  { path: '/community/:board', name: 'community-board', component: p('community/CommunityHome') },
  { path: '/community/:board/:id', name: 'community-post', component: p('community/PostDetail') },

  // ── Q&A ──
  { path: '/qa', name: 'qa', component: p('qa/QaList') },
  { path: '/qa/write', name: 'qa-write', component: p('qa/QAWrite'), meta: { auth: true } },
  { path: '/qa/:id', name: 'qa-detail', component: p('qa/QaDetail') },

  // ── Jobs ──
  { path: '/jobs', name: 'jobs', component: p('jobs/JobList') },
  { path: '/jobs/write', name: 'job-write', component: p('jobs/JobWrite'), meta: { auth: true } },
  { path: '/jobs/:id', name: 'job-detail', component: p('jobs/JobDetail') },

  // ── Market ──
  { path: '/market', name: 'market', component: p('market/MarketList') },
  { path: '/market/write', name: 'market-write', component: p('market/MarketWrite'), meta: { auth: true } },
  { path: '/market/:id', name: 'market-detail', component: p('market/MarketDetail') },

  // ── Real Estate ──
  { path: '/realestate', name: 'realestate', component: p('realestate/RealEstateList') },
  { path: '/realestate/write', name: 'realestate-write', component: p('realestate/RealEstateWrite'), meta: { auth: true } },
  { path: '/realestate/:id', name: 'realestate-detail', component: p('realestate/RealEstateDetail') },

  // ── Clubs ──
  { path: '/clubs', name: 'clubs', component: p('community/ClubList') },
  { path: '/clubs/:id', name: 'club-detail', component: p('community/ClubDetail') },

  // ── News ──
  { path: '/news', name: 'news', component: p('news/NewsList') },
  { path: '/news/:id', name: 'news-detail', component: p('news/NewsDetail') },

  // ── Recipes ──
  { path: '/recipes', name: 'recipes', component: p('recipes/RecipeList') },
  { path: '/recipes/write', name: 'recipe-create', component: p('recipes/RecipeCreate'), meta: { auth: true } },
  { path: '/recipes/:id', name: 'recipe-detail', component: p('recipes/RecipeDetail') },

  // ── Group Buy ──
  { path: '/groupbuy', name: 'groupbuy', component: p('groupbuy/GroupBuyHome') },

  // ── Events ──
  { path: '/events', name: 'events', component: p('events/EventList') },
  { path: '/events/create', name: 'event-create', component: p('events/EventCreate'), meta: { auth: true } },
  { path: '/events/:id', name: 'event-detail', component: p('events/EventDetail') },

  // ── Directory (Business) ──
  { path: '/directory', name: 'directory', component: p('directory/BusinessList') },
  { path: '/directory/register', name: 'business-register', component: p('directory/BusinessRegister'), meta: { auth: true } },
  { path: '/directory/:id', name: 'business-detail', component: p('directory/BusinessDetail') },

  // ── Chat ──
  { path: '/chat', name: 'chat-rooms', component: p('chat/ChatRooms'), meta: { auth: true } },
  { path: '/chat/:id', name: 'chat-room', component: p('chat/ChatRoom'), meta: { auth: true } },

  // ── Games ──
  { path: '/games', name: 'games', component: p('games/GameLobby') },
  { path: '/games/quiz', name: 'game-quiz', component: p('games/QuizGame'), meta: { auth: true } },
  { path: '/games/memory', name: 'game-memory', component: p('games/MemoryGame') },
  { path: '/games/bingo', name: 'game-bingo', component: p('games/BingoGame') },
  { path: '/games/2048', name: 'game-2048', component: p('games/Game2048') },
  { path: '/games/omok', name: 'game-omok', component: p('games/OmokGame') },
  { path: '/games/gostop', name: 'game-gostop', component: p('games/GoStopSolo') },
  { path: '/games/holdem', name: 'game-holdem', component: p('games/HoldemSolo') },
  { path: '/games/poker', name: 'game-poker', component: p('games/Poker'), meta: { auth: true } },
  { path: '/games/blackjack', name: 'game-blackjack', component: p('games/Blackjack') },
  { path: '/games/hangul', name: 'game-hangul', component: p('games/GameHangul') },
  { path: '/games/wordle', name: 'game-wordle', component: p('games/GameWordle') },
  { path: '/games/counting', name: 'game-counting', component: p('games/GameCounting') },
  { path: '/games/colors', name: 'game-colors', component: p('games/GameColors') },
  { path: '/games/idiom', name: 'game-idiom', component: p('games/GameIdiom') },
  { path: '/games/flag', name: 'game-flag', component: p('games/GameFlag') },
  { path: '/games/snake', name: 'game-snake', component: p('games/GameSnake') },
  { path: '/games/typing', name: 'game-typing', component: p('games/GameTyping') },
  { path: '/games/spelling', name: 'game-spelling', component: p('games/GameSpelling') },
  { path: '/games/proverb', name: 'game-proverb', component: p('games/GameProverb') },
  { path: '/games/wordchain', name: 'game-wordchain', component: p('games/GameWordChain') },
  { path: '/games/wordblank', name: 'game-wordblank', component: p('games/GameWordBlank') },
  { path: '/games/wordcard', name: 'game-wordcard', component: p('games/GameWordCard') },
  { path: '/games/satwords', name: 'game-satwords', component: p('games/GameSATWords') },
  { path: '/games/stroop', name: 'game-stroop', component: p('games/GameStroop') },
  { path: '/games/puzzle', name: 'game-puzzle', component: p('games/GamePuzzle') },
  { path: '/games/shapes', name: 'game-shapes', component: p('games/GameShapes') },
  { path: '/games/speedcalc', name: 'game-speedcalc', component: p('games/GameSpeedCalc') },
  { path: '/games/stocksim', name: 'game-stocksim', component: p('games/GameStockSim') },
  { path: '/games/uslife', name: 'game-uslife', component: p('games/GameUSLife') },
  { path: '/games/seniormemory', name: 'game-seniormemory', component: p('games/GameSeniorMemory') },
  { path: '/games/towerdefense', name: 'game-towerdefense', component: p('games/GameTowerDefense') },
  { path: '/games/slots', name: 'game-slots', component: p('games/GameSlots') },
  { path: '/games/leaderboard', name: 'game-leaderboard', component: p('games/Leaderboard') },
  { path: '/games/shop', name: 'point-shop', component: p('games/PointShop'), meta: { auth: true } },

  // ── Shorts ──
  { path: '/shorts', name: 'shorts', component: p('shorts/ShortsHome') },
  { path: '/shorts/upload', name: 'shorts-upload', component: p('shorts/ShortsUpload'), meta: { auth: true } },

  // ── Music ──
  { path: '/music', name: 'music', component: p('music/MusicHome') },

  // ── Elder Safety ──
  { path: '/elder', name: 'elder', component: p('elder/ElderHome'), meta: { auth: true } },
  { path: '/elder/checkin', name: 'elder-checkin', component: p('elder/ElderCheckin'), meta: { auth: true } },
  { path: '/elder/guardian', name: 'elder-guardian', component: p('elder/GuardianDashboard'), meta: { auth: true } },

  // ── Friends ──
  { path: '/friends', name: 'friends', component: p('friends/FriendList'), meta: { auth: true } },

  // ── Messages ──
  { path: '/messages', name: 'messages', component: p('messages/MessageInbox'), meta: { auth: true } },

  // ── Notifications ──
  { path: '/notifications', name: 'notifications', component: p('Notifications'), meta: { auth: true } },

  // ── Points ──
  { path: '/points', name: 'points', component: p('points/PointDashboard'), meta: { auth: true } },
  { path: '/points/rules', name: 'point-rules', component: p('PointRules') },

  // ── Search ──
  { path: '/search', name: 'search', component: p('Search') },

  // ── Profile ──
  { path: '/profile/edit', name: 'profile-edit', component: p('profile/ProfileEdit'), meta: { auth: true } },
  { path: '/profile/:id', name: 'profile', component: p('profile/UserProfile') },
  { path: '/dashboard', name: 'dashboard', component: p('profile/UserDashboard'), meta: { auth: true } },

  // ── Admin ──
  {
    path: '/admin',
    component: p('admin/AdminLayout'),
    meta: { auth: true, admin: true },
    children: [
      { path: '', name: 'admin', component: p('admin/Overview') },
      { path: 'members', name: 'admin-members', component: p('admin/Members') },
      { path: 'users', name: 'admin-users', component: p('admin/Users') },
      { path: 'content', name: 'admin-content', component: p('admin/Content') },
      { path: 'boards', name: 'admin-boards', component: p('admin/BoardManager') },
      { path: 'community', name: 'admin-community', component: p('admin/Dashboard') },
      { path: 'news', name: 'admin-news', component: p('admin/AdminNews') },
      { path: 'jobs', name: 'admin-jobs', component: p('admin/AdminJobs') },
      { path: 'market', name: 'admin-market', component: p('admin/AdminMarket') },
      { path: 'realestate', name: 'admin-realestate', component: p('admin/AdminRealestate') },
      { path: 'clubs', name: 'admin-clubs', component: p('admin/AdminClubs') },
      { path: 'qa', name: 'admin-qa', component: p('admin/AdminQa') },
      { path: 'recipes', name: 'admin-recipes', component: p('admin/AdminRecipes') },
      { path: 'events', name: 'admin-events', component: p('admin/AdminEvents') },
      { path: 'shopping', name: 'admin-shopping', component: p('admin/AdminShopping') },
      { path: 'shorts', name: 'admin-shorts', component: p('admin/AdminShorts') },
      { path: 'directory', name: 'admin-directory', component: p('admin/Business') },
      { path: 'games', name: 'admin-games', component: p('admin/AdminGames') },
      { path: 'music', name: 'admin-music', component: p('admin/AdminMusic') },
      { path: 'groupbuy', name: 'admin-groupbuy', component: p('admin/GroupBuy') },
      { path: 'elder', name: 'admin-elder', component: p('admin/Elder') },
      { path: 'friends', name: 'admin-friends', component: p('admin/AdminFriends') },
      { path: 'chats', name: 'admin-chats', component: p('admin/Chats') },
      { path: 'banners', name: 'admin-banners', component: p('admin/Banners') },
      { path: 'payments', name: 'admin-payments', component: p('admin/Payments') },
      { path: 'security', name: 'admin-security', component: p('admin/AdminSecurity') },
      { path: 'settings', name: 'admin-settings', component: p('admin/SiteSettings') },
      { path: 'system', name: 'admin-system', component: p('admin/System') },
    ]
  },

  // ── 404 ──
  { path: '/404', name: 'not-found', component: p('NotFound') },
  { path: '/:pathMatch(.*)*', redirect: '/404' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

// ── Navigation Guards ──
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Wait for auth initialization to complete
  await authStore.initPromise

  // Auth required but not logged in
  if (to.meta.auth && !authStore.isLoggedIn) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Admin required but not admin
  if (to.meta.admin && !authStore.isAdmin) {
    return next({ name: 'home' })
  }

  // Guest-only page but already logged in
  if (to.meta.guest && authStore.isLoggedIn) {
    return next({ name: 'home' })
  }

  next()
})

// ── Chunk load error handler (auto-refresh on stale builds) ──
router.onError((err) => {
  const isChunkError =
    err?.message?.includes('Failed to fetch dynamically imported module') ||
    err?.message?.includes('Loading chunk') ||
    err?.name === 'ChunkLoadError'

  if (isChunkError) {
    const lastReload = sessionStorage.getItem('_chunk_reload')
    const now = Date.now()
    if (!lastReload || now - Number(lastReload) > 10000) {
      sessionStorage.setItem('_chunk_reload', String(now))
      window.location.reload()
    }
  }
})

export default router
