<?php

use App\Http\Controllers\API\AuthController;
use App\Http\Controllers\API\PostController;
use App\Http\Controllers\API\BoardController;
use App\Http\Controllers\API\JobController;
use App\Http\Controllers\API\MarketController;
use App\Http\Controllers\API\MarketReservationController;
use App\Http\Controllers\API\BusinessController;
use App\Http\Controllers\API\BusinessClaimController;
use App\Http\Controllers\API\RealEstateController;
use App\Http\Controllers\API\ClubController;
use App\Http\Controllers\API\NewsController;
use App\Http\Controllers\API\RecipeController;
use App\Http\Controllers\API\GroupBuyController;
use App\Http\Controllers\API\EventController;
use App\Http\Controllers\API\QaController;
use App\Http\Controllers\API\ShortController;
use App\Http\Controllers\API\ShoppingController;
use App\Http\Controllers\API\MusicController;
use App\Http\Controllers\API\SearchController;
use App\Http\Controllers\API\CommentController;
use App\Http\Controllers\API\ProfileController;
use App\Http\Controllers\API\UserLocationController;
use App\Http\Controllers\API\PointController;
use App\Http\Controllers\API\BookmarkController;
use App\Http\Controllers\API\ChatController;
use App\Http\Controllers\API\FriendController;
use App\Http\Controllers\API\MessageController;
use App\Http\Controllers\API\NotificationController;
use App\Http\Controllers\API\PaymentController;
use App\Http\Controllers\API\ReportController;
use App\Http\Controllers\API\GameController;
use App\Http\Controllers\API\GameScoreController;
use App\Http\Controllers\API\ElderController;
use App\Http\Controllers\API\AdminController;
use App\Http\Controllers\API\AdminBusinessController;
use App\Http\Controllers\API\AdminQaController;
use App\Http\Controllers\API\AdminRecipeController;
use App\Http\Controllers\API\AdminSettingsController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
| All routes are automatically prefixed with /api by RouteServiceProvider.
*/

// ─── Public: Auth ────────────────────────────────────────────────────────────
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login',    [AuthController::class, 'login']);

// ─── Public: Site Settings ───────────────────────────────────────────────────
Route::get('/settings/public', [AdminSettingsController::class, 'getPublicSettings']);
Route::get('/site-settings/logo', [AdminSettingsController::class, 'getLogo']);

// ─── Public: Read-Only ───────────────────────────────────────────────────────
Route::get('/posts',                     [PostController::class, 'index']);
Route::get('/posts/{id}',                [PostController::class, 'show']);
Route::get('/boards',                    [BoardController::class, 'index']);
Route::get('/jobs',                      [JobController::class, 'index']);
Route::get('/jobs/{id}',                 [JobController::class, 'show']);
Route::get('/market',                    [MarketController::class, 'index']);
Route::get('/market/{id}',              [MarketController::class, 'show']);
Route::get('/businesses',                [BusinessController::class, 'index']);
Route::get('/businesses/{id}',           [BusinessController::class, 'show']);
Route::get('/businesses/{id}/reviews',   [BusinessController::class, 'reviews']);
Route::get('/realestate',                [RealEstateController::class, 'index']);
Route::get('/realestate/{id}',           [RealEstateController::class, 'show']);
Route::get('/clubs',                     [ClubController::class, 'index']);
Route::get('/clubs/{id}',                [ClubController::class, 'show']);
Route::get('/clubs/{id}/posts',          [ClubController::class, 'posts']);
Route::get('/news',                      [NewsController::class, 'index']);
Route::get('/news/categories',           [NewsController::class, 'categories']);
Route::get('/news/{id}',                 [NewsController::class, 'show']);
Route::get('/recipes',                   [RecipeController::class, 'index']);
Route::get('/recipes/categories',        [RecipeController::class, 'categories']);
Route::get('/recipes/{id}',             [RecipeController::class, 'show']);
Route::get('/groupbuys',                 [GroupBuyController::class, 'index']);
Route::get('/groupbuys/{id}',            [GroupBuyController::class, 'show']);
Route::get('/events',                    [EventController::class, 'index']);
Route::get('/events/{id}',              [EventController::class, 'show']);
Route::get('/qa',                        [QaController::class, 'index']);
Route::get('/qa/categories',             [QaController::class, 'categories']);
Route::get('/qa/{id}',                   [QaController::class, 'show']);
Route::get('/shorts',                    [ShortController::class, 'index']);
Route::get('/shopping',                  [ShoppingController::class, 'index']);
Route::get('/music/categories',          [MusicController::class, 'categories']);
Route::get('/music/tracks/{categoryId}', [MusicController::class, 'tracks']);
Route::get('/search',                    [SearchController::class, 'search']);
Route::get('/comments/{type}/{id}',      [CommentController::class, 'index']);

// ─── Authenticated Routes ────────────────────────────────────────────────────
Route::middleware('auth:sanctum')->group(function () {

    // Auth
    Route::post('/logout',          [AuthController::class, 'logout']);
    Route::get('/user',             [AuthController::class, 'user']);

    // Profile
    Route::put('/user/profile',     [ProfileController::class, 'update']);
    Route::post('/user/avatar',     [ProfileController::class, 'uploadAvatar']);
    Route::put('/user/location',    [UserLocationController::class, 'update']);

    // Posts CRUD
    Route::post('/posts',           [PostController::class, 'store']);
    Route::put('/posts/{id}',       [PostController::class, 'update']);
    Route::delete('/posts/{id}',    [PostController::class, 'destroy']);
    Route::post('/posts/{id}/like', [PostController::class, 'toggleLike']);

    // Jobs CRUD
    Route::post('/jobs',            [JobController::class, 'store']);
    Route::put('/jobs/{id}',        [JobController::class, 'update']);
    Route::delete('/jobs/{id}',     [JobController::class, 'destroy']);

    // Market CRUD
    Route::post('/market',                              [MarketController::class, 'store']);
    Route::put('/market/{id}',                          [MarketController::class, 'update']);
    Route::delete('/market/{id}',                       [MarketController::class, 'destroy']);
    Route::post('/market/{id}/reserve',                 [MarketReservationController::class, 'reserve']);
    Route::post('/market/reservations/{id}/complete',   [MarketReservationController::class, 'complete']);
    Route::post('/market/reservations/{id}/cancel',     [MarketReservationController::class, 'cancel']);

    // Business
    Route::post('/businesses',                [BusinessController::class, 'store']);
    Route::put('/businesses/{id}',            [BusinessController::class, 'update']);
    Route::post('/businesses/{id}/reviews',   [BusinessController::class, 'storeReview']);
    Route::post('/businesses/claim',          [BusinessClaimController::class, 'store']);

    // Real Estate
    Route::post('/realestate',       [RealEstateController::class, 'store']);
    Route::put('/realestate/{id}',   [RealEstateController::class, 'update']);
    Route::delete('/realestate/{id}',[RealEstateController::class, 'destroy']);

    // Clubs
    Route::post('/clubs',                [ClubController::class, 'store']);
    Route::put('/clubs/{id}',            [ClubController::class, 'update']);
    Route::post('/clubs/{id}/join',      [ClubController::class, 'join']);
    Route::post('/clubs/{id}/leave',     [ClubController::class, 'leave']);
    Route::post('/clubs/{id}/posts',     [ClubController::class, 'storePost']);

    // Recipes
    Route::post('/recipes',          [RecipeController::class, 'store']);
    Route::put('/recipes/{id}',      [RecipeController::class, 'update']);
    Route::delete('/recipes/{id}',   [RecipeController::class, 'destroy']);

    // GroupBuy
    Route::post('/groupbuys',            [GroupBuyController::class, 'store']);
    Route::post('/groupbuys/{id}/join',  [GroupBuyController::class, 'join']);

    // Events
    Route::post('/events',               [EventController::class, 'store']);
    Route::post('/events/{id}/attend',   [EventController::class, 'toggleAttend']);

    // Q&A
    Route::post('/qa',                          [QaController::class, 'store']);
    Route::post('/qa/{id}/answer',              [QaController::class, 'answer']);
    Route::post('/qa/{id}/accept/{answerId}',   [QaController::class, 'acceptAnswer']);

    // Shorts
    Route::post('/shorts',           [ShortController::class, 'store']);
    Route::post('/shorts/{id}/like', [ShortController::class, 'toggleLike']);

    // Comments (polymorphic)
    Route::post('/comments',             [CommentController::class, 'store']);
    Route::put('/comments/{id}',         [CommentController::class, 'update']);
    Route::delete('/comments/{id}',      [CommentController::class, 'destroy']);
    Route::post('/comments/{id}/like',   [CommentController::class, 'toggleLike']);

    // Bookmarks
    Route::post('/bookmarks',   [BookmarkController::class, 'toggle']);
    Route::get('/bookmarks',    [BookmarkController::class, 'index']);

    // Chat
    Route::get('/chat/rooms',                [ChatController::class, 'rooms']);
    Route::post('/chat/rooms',               [ChatController::class, 'createRoom']);
    Route::get('/chat/rooms/{id}/messages',  [ChatController::class, 'messages']);
    Route::post('/chat/rooms/{id}/messages', [ChatController::class, 'sendMessage']);

    // Friends
    Route::get('/friends',                      [FriendController::class, 'index']);
    Route::post('/friends/request/{userId}',    [FriendController::class, 'sendRequest']);
    Route::post('/friends/accept/{id}',         [FriendController::class, 'accept']);
    Route::post('/friends/block/{userId}',      [FriendController::class, 'block']);
    Route::delete('/friends/{id}',              [FriendController::class, 'remove']);

    // Messages (DM)
    Route::get('/messages',     [MessageController::class, 'index']);
    Route::post('/messages',    [MessageController::class, 'store']);

    // Notifications
    Route::get('/notifications',            [NotificationController::class, 'index']);
    Route::post('/notifications/read',      [NotificationController::class, 'markRead']);
    Route::post('/notifications/{id}/read', [NotificationController::class, 'markOneRead']);

    // Points
    Route::get('/points/history',       [PointController::class, 'history']);
    Route::get('/points/balance',       [PointController::class, 'balance']);
    Route::post('/points/daily-spin',   [PointController::class, 'dailySpin']);

    // Payments (Stripe)
    Route::post('/payments/create-intent', [PaymentController::class, 'createIntent']);
    Route::post('/payments/confirm',       [PaymentController::class, 'confirm']);

    // Report
    Route::post('/reports', [ReportController::class, 'store']);

    // Games
    Route::get('/games/settings',           [GameController::class, 'settings']);
    Route::post('/games/scores',            [GameScoreController::class, 'store']);
    Route::get('/games/leaderboard/{game}', [GameScoreController::class, 'leaderboard']);
    Route::get('/games/rooms',              [GameController::class, 'rooms']);
    Route::post('/games/rooms',             [GameController::class, 'createRoom']);
    Route::post('/games/rooms/{id}/join',   [GameController::class, 'joinRoom']);

    // Music playlists
    Route::get('/music/playlists',                          [MusicController::class, 'playlists']);
    Route::post('/music/playlists',                         [MusicController::class, 'createPlaylist']);
    Route::post('/music/playlists/{id}/tracks',             [MusicController::class, 'addTrack']);
    Route::delete('/music/playlists/{id}/tracks/{trackId}', [MusicController::class, 'removeTrack']);

    // Elder
    Route::get('/elder/settings',           [ElderController::class, 'settings']);
    Route::put('/elder/settings',           [ElderController::class, 'updateSettings']);
    Route::post('/elder/checkin',           [ElderController::class, 'checkin']);
    Route::post('/elder/sos',              [ElderController::class, 'sos']);
    Route::get('/elder/guardian/wards',     [ElderController::class, 'guardianWards']);
    Route::get('/elder/checkin-history',    [ElderController::class, 'checkinHistory']);

    // User profile view
    Route::get('/users/{id}',       [ProfileController::class, 'show']);
    Route::get('/users/{id}/posts', [ProfileController::class, 'posts']);
});

// ─── Admin Routes ────────────────────────────────────────────────────────────
Route::middleware(['auth:sanctum', 'admin'])->prefix('admin')->group(function () {

    // Overview & Stats
    Route::get('/overview', [AdminController::class, 'overview']);
    Route::get('/stats',    [AdminController::class, 'stats']);

    // User Management
    Route::get('/users',                [AdminController::class, 'users']);
    Route::put('/users/{id}',           [AdminController::class, 'updateUser']);
    Route::delete('/users/{id}',        [AdminController::class, 'deleteUser']);
    Route::post('/users/{id}/ban',      [AdminController::class, 'banUser']);
    Route::post('/users/{id}/unban',    [AdminController::class, 'unbanUser']);
    Route::post('/users/{id}/make-admin', [AdminController::class, 'makeAdmin']);

    // Posts
    Route::get('/posts',            [AdminController::class, 'posts']);
    Route::delete('/posts/{id}',    [AdminController::class, 'deletePost']);
    Route::post('/posts/{id}/pin',  [AdminController::class, 'pinPost']);
    Route::post('/posts/{id}/hide', [AdminController::class, 'hidePost']);

    // Boards
    Route::get('/boards',           [AdminController::class, 'boards']);
    Route::post('/boards',          [AdminController::class, 'createBoard']);
    Route::put('/boards/{id}',      [AdminController::class, 'updateBoard']);
    Route::delete('/boards/{id}',   [AdminController::class, 'deleteBoard']);

    // Jobs
    Route::get('/jobs',             [AdminController::class, 'jobs']);
    Route::delete('/jobs/{id}',     [AdminController::class, 'deleteJob']);

    // Market
    Route::get('/market',           [AdminController::class, 'marketItems']);
    Route::delete('/market/{id}',   [AdminController::class, 'deleteMarketItem']);

    // Businesses
    Route::get('/businesses',                       [AdminBusinessController::class, 'index']);
    Route::put('/businesses/{id}',                  [AdminBusinessController::class, 'update']);
    Route::delete('/businesses/{id}',               [AdminBusinessController::class, 'destroy']);
    Route::get('/business-claims',                  [AdminBusinessController::class, 'claims']);
    Route::post('/business-claims/{id}/approve',    [AdminBusinessController::class, 'approveClaim']);
    Route::post('/business-claims/{id}/reject',     [AdminBusinessController::class, 'rejectClaim']);

    // Real Estate
    Route::get('/realestate',           [AdminController::class, 'realestate']);
    Route::delete('/realestate/{id}',   [AdminController::class, 'deleteRealestate']);

    // Clubs
    Route::get('/clubs',            [AdminController::class, 'clubs']);
    Route::delete('/clubs/{id}',    [AdminController::class, 'deleteClub']);

    // News
    Route::get('/news',             [AdminController::class, 'news']);
    Route::delete('/news/{id}',     [AdminController::class, 'deleteNews']);

    // Q&A
    Route::get('/qa',               [AdminQaController::class, 'index']);
    Route::delete('/qa/{id}',       [AdminQaController::class, 'destroy']);

    // Recipes
    Route::get('/recipes',          [AdminRecipeController::class, 'index']);
    Route::delete('/recipes/{id}',  [AdminRecipeController::class, 'destroy']);

    // Events
    Route::get('/events',           [AdminController::class, 'events']);
    Route::delete('/events/{id}',   [AdminController::class, 'deleteEvent']);

    // Shorts
    Route::get('/shorts',           [AdminController::class, 'shorts']);
    Route::delete('/shorts/{id}',   [AdminController::class, 'deleteShort']);

    // Shopping
    Route::get('/shopping',         [AdminController::class, 'shopping']);

    // Reports
    Route::get('/reports',          [AdminController::class, 'reports']);
    Route::put('/reports/{id}',     [AdminController::class, 'updateReport']);

    // Chats
    Route::get('/chats',            [AdminController::class, 'chats']);

    // Banners
    Route::get('/banners',          [AdminController::class, 'banners']);
    Route::post('/banners',         [AdminController::class, 'createBanner']);
    Route::put('/banners/{id}',     [AdminController::class, 'updateBanner']);
    Route::delete('/banners/{id}',  [AdminController::class, 'deleteBanner']);

    // Settings
    Route::get('/settings',         [AdminSettingsController::class, 'index']);
    Route::put('/settings',         [AdminSettingsController::class, 'update']);
    Route::post('/settings/logo',   [AdminSettingsController::class, 'uploadLogo']);

    // Security
    Route::get('/ip-bans',          [AdminController::class, 'ipBans']);
    Route::post('/ip-bans',         [AdminController::class, 'createIpBan']);
    Route::delete('/ip-bans/{id}',  [AdminController::class, 'deleteIpBan']);

    // Games admin
    Route::get('/games/settings',   [AdminController::class, 'gameSettings']);
    Route::put('/games/settings',   [AdminController::class, 'updateGameSettings']);

    // Payments
    Route::get('/payments',         [AdminController::class, 'payments']);

    // Elder admin
    Route::get('/elder/users',      [AdminController::class, 'elderUsers']);

    // Music admin
    Route::post('/music/categories',        [MusicController::class, 'storeCategory']);
    Route::post('/music/tracks',            [MusicController::class, 'storeTrack']);
    Route::delete('/music/tracks/{id}',     [MusicController::class, 'destroyTrack']);
});
