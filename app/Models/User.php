<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Tymon\JWTAuth\Contracts\JWTSubject;

class User extends Authenticatable implements JWTSubject
{
    use HasFactory, Notifiable;

    protected $fillable = [
        'name', 'nickname', 'email', 'password', 'phone',
        'address', 'city', 'state', 'zipcode', 'latitude', 'longitude', 'default_radius',
        'avatar', 'bio', 'language', 'points', 'game_points',
        'address1', 'address2',
        'role', 'is_banned', 'ban_reason', 'allow_friend_request', 'allow_messages', 'allow_elder_service',
        'last_login_at', 'last_active_at', 'login_count',
        'provider', 'provider_id',
        'fcm_token', 'push_platform',
    ];

    protected $hidden = ['password', 'remember_token'];

    protected $appends = ['display_name'];

    /**
     * 표시 이름: 닉네임 → 이메일 앞부분 → 실명 순서
     */
    public function getDisplayNameAttribute(): string
    {
        if ($this->nickname) return $this->nickname;
        if ($this->email) return explode('@', $this->email)[0];
        return $this->attributes['name'] ?? '회원';
    }

    /**
     * API 응답에서 name → display_name으로 자동 교체
     * 실명은 real_name 필드로 별도 접근 가능 (부동산 등)
     */
    public function toArray()
    {
        $array = parent::toArray();
        $array['real_name'] = $this->attributes['name'] ?? '';
        $array['name'] = $this->display_name; // name 필드를 display_name으로 대체
        return $array;
    }

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'last_login_at' => 'datetime',
            'password' => 'hashed',
            'is_banned' => 'boolean',
            'points' => 'integer',
            'game_points' => 'integer',
            'login_count' => 'integer',
            'latitude' => 'decimal:7',
            'longitude' => 'decimal:7',
            'allow_friend_request' => 'boolean',
            'allow_messages' => 'boolean',
            'allow_elder_service' => 'boolean',
        ];
    }

    // JWT
    public function getJWTIdentifier() { return $this->getKey(); }
    public function getJWTCustomClaims() { return []; }

    // Accessors
    public function getIsAdminAttribute(): bool { return in_array($this->role, ['admin', 'super_admin', 'moderator']); }

    // Relationships
    public function posts() { return $this->hasMany(Post::class); }
    public function jobPosts() { return $this->hasMany(JobPost::class); }
    public function marketItems() { return $this->hasMany(MarketItem::class); }
    public function clubs() { return $this->hasMany(Club::class); }
    public function pointLogs() { return $this->hasMany(PointLog::class); }
    public function notifications() { return $this->hasMany(Notification::class); }
    public function friends() { return $this->hasMany(Friend::class); }
    public function elderSetting() { return $this->hasOne(ElderSetting::class); }

    // Distance scope (miles)
    public function scopeNearby($query, $lat, $lng, $radius = 50)
    {
        return $query->selectRaw("*, (3959 * acos(cos(radians(?)) * cos(radians(latitude)) * cos(radians(longitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance", [$lat, $lng, $lat])
            ->having('distance', '<', $radius)
            ->orderBy('distance');
    }

    // Helper
    public function addPoints(int $amount, string $reason, string $type = 'earn')
    {
        $this->increment('points', $amount);
        $this->pointLogs()->create([
            'amount' => $amount,
            'type' => $type,
            'reason' => $reason,
            'balance_after' => $this->fresh()->points,
        ]);
    }
}
