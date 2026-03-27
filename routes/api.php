<?php
use App\Http\Controllers\API\AuthController;
use App\Http\Controllers\API\PostController;
use App\Http\Controllers\API\CommentController;
use App\Http\Controllers\API\JobController;
use App\Http\Controllers\API\MarketController;
use App\Http\Controllers\API\BusinessController;
use App\Http\Controllers\API\PointController;
use App\Http\Controllers\API\MessageController;
use App\Http\Controllers\API\AdminController;
use App\Http\Controllers\API\BoardController;
use Illuminate\Support\Facades\Route;

// 인증 (Public)
Route::prefix('auth')->group(function () {
    Route::post('register', [AuthController::class, 'register']);
    Route::post('login',    [AuthController::class, 'login']);
});

// 공개 조회
Route::get('boards',              [BoardController::class, 'index']);
Route::get('boards/{board}',      [BoardController::class, 'show']);
Route::get('posts',               [PostController::class, 'index']);
Route::get('posts/{post}',        [PostController::class, 'show']);
Route::get('jobs',                [JobController::class, 'index']);
Route::get('jobs/{job}',          [JobController::class, 'show']);
Route::get('market',              [MarketController::class, 'index']);
Route::get('market/{item}',       [MarketController::class, 'show']);
Route::get('businesses',          [BusinessController::class, 'index']);
Route::get('businesses/{business}',[BusinessController::class, 'show']);

// 인증 필요
Route::middleware('auth:api')->group(function () {
    // Auth
    Route::post('auth/logout',  [AuthController::class, 'logout']);
    Route::post('auth/refresh', [AuthController::class, 'refresh']);
    Route::get('auth/me',       [AuthController::class, 'me']);

    // Posts
    Route::post('posts',             [PostController::class, 'store']);
    Route::put('posts/{post}',       [PostController::class, 'update']);
    Route::delete('posts/{post}',    [PostController::class, 'destroy']);
    Route::post('posts/{post}/like', [PostController::class, 'like']);

    // Comments
    Route::post('posts/{post}/comments',    [CommentController::class, 'store']);
    Route::delete('comments/{comment}',     [CommentController::class, 'destroy']);

    // Jobs
    Route::post('jobs',          [JobController::class, 'store']);
    Route::delete('jobs/{job}',  [JobController::class, 'destroy']);

    // Market
    Route::post('market',             [MarketController::class, 'store']);
    Route::put('market/{item}',       [MarketController::class, 'update']);
    Route::delete('market/{item}',    [MarketController::class, 'destroy']);

    // Businesses
    Route::post('businesses',                      [BusinessController::class, 'store']);
    Route::post('businesses/{business}/review',    [BusinessController::class, 'review']);

    // Points
    Route::get('points/balance',  [PointController::class, 'balance']);
    Route::get('points/history',  [PointController::class, 'history']);
    Route::post('points/checkin', [PointController::class, 'checkin']);
    Route::post('points/convert', [PointController::class, 'convert']);

    // Messages
    Route::get('messages/inbox',         [MessageController::class, 'inbox']);
    Route::get('messages/unread',        [MessageController::class, 'unreadCount']);
    Route::post('messages',              [MessageController::class, 'send']);
    Route::get('messages/{message}',     [MessageController::class, 'show']);

    // Admin
    Route::middleware('admin')->prefix('admin')->group(function () {
        Route::get('stats',                      [AdminController::class, 'stats']);
        Route::get('users',                      [AdminController::class, 'users']);
        Route::post('users/{user}/ban',          [AdminController::class, 'banUser']);
        Route::post('users/{user}/unban',        [AdminController::class, 'unbanUser']);
        Route::get('reports',                    [AdminController::class, 'reports']);
        Route::post('reports/{report}/dismiss',  [AdminController::class, 'dismissReport']);
    });
});
