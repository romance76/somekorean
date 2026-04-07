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

// Poker channels (public - any logged in user)
Broadcast::channel('poker.lobby', function ($user) {
    return auth()->check();
});

Broadcast::channel('poker.tournament.{tournamentId}', function ($user, $tournamentId) {
    return auth()->check();
});

Broadcast::channel('poker.table.{tableId}', function ($user, $tableId) {
    return auth()->check();
});
