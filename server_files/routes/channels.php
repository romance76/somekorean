<?php

use Illuminate\Support\Facades\Broadcast;

Broadcast::channel('App.Models.User.{id}', function ($user, $id) {
    return (int) $user->id === (int) $id;
});

// Chat channels - public (anyone logged in can listen)
Broadcast::channel('chat.{roomId}', function ($user, $roomId) {
    return auth()->check();
});

// WebRTC private call channel
Broadcast::channel('call.{userId}', function ($user, $userId) {
    return (int) $user->id === (int) $userId;
});
