## Business Claim Routes (auth:api middleware)
Route::post('businesses/{id}/claim', [BusinessClaimController::class, 'initiate']);
Route::post('claims/{id}/email', [BusinessClaimController::class, 'sendEmailVerification']);
Route::get('claims/email/verify/{token}', [BusinessClaimController::class, 'verifyEmail']); // PUBLIC
Route::post('claims/{id}/documents', [BusinessClaimController::class, 'uploadDocuments']);
Route::get('claims/{id}/status', [BusinessClaimController::class, 'status']);
Route::get('my-claims', [BusinessClaimController::class, 'myClaims']);

## Owner Dashboard Routes (auth:api middleware)
Route::get('owner/business', [OwnerDashboardController::class, 'myBusiness']);
Route::put('owner/business', [OwnerDashboardController::class, 'update']);
Route::post('owner/business/photos', [OwnerDashboardController::class, 'uploadPhotos']);
Route::put('owner/business/photos/reorder', [OwnerDashboardController::class, 'reorderPhotos']);
Route::delete('owner/business/photos/{index}', [OwnerDashboardController::class, 'deletePhoto']);
Route::post('owner/business/menu-item', [OwnerDashboardController::class, 'upsertMenuItem']);
Route::delete('owner/business/menu-item/{itemId}', [OwnerDashboardController::class, 'deleteMenuItem']);
Route::get('owner/reviews', [OwnerDashboardController::class, 'myReviews']);
Route::post('owner/reviews/{id}/reply', [OwnerDashboardController::class, 'replyReview']);
Route::post('owner/reviews/{id}/report', [OwnerDashboardController::class, 'reportReview']);
Route::get('owner/events', [OwnerDashboardController::class, 'myEvents']);
Route::post('owner/events', [OwnerDashboardController::class, 'createEvent']);
Route::delete('owner/events/{id}', [OwnerDashboardController::class, 'deleteEvent']);
Route::get('owner/stats', [OwnerDashboardController::class, 'stats']);

## Admin Business Routes (admin middleware)
Route::get('businesses-list', [AdminBusinessController::class, 'index']);
Route::get('businesses-list/{id}', [AdminBusinessController::class, 'show']);
Route::put('businesses-list/{id}', [AdminBusinessController::class, 'update']);
Route::delete('businesses-list/{id}', [AdminBusinessController::class, 'destroy']);
Route::get('business-claims-list', [AdminBusinessController::class, 'claims']);
Route::post('business-claims-list/{id}/approve', [AdminBusinessController::class, 'approveClaim']);
Route::post('business-claims-list/{id}/reject', [AdminBusinessController::class, 'rejectClaim']);
Route::get('business-reviews-list', [AdminBusinessController::class, 'reviews']);
Route::post('business-reviews-list/{id}/hide', [AdminBusinessController::class, 'hideReview']);
Route::post('business-reviews-list/{id}/restore', [AdminBusinessController::class, 'restoreReview']);
Route::delete('business-reviews-list/{id}', [AdminBusinessController::class, 'deleteReview']);
Route::post('businesses/import', [AdminBusinessController::class, 'bulkImport']);
