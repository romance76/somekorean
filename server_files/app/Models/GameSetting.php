<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class GameSetting extends Model
{
    protected $fillable = [
        'key', 'value', 'description', 'updated_by',
    ];

    public function updatedByUser()
    {
        return $this->belongsTo(User::class, 'updated_by');
    }

    /**
     * 설정값 조회
     */
    public static function get(string $key, mixed $default = null): mixed
    {
        $setting = static::where('key', $key)->first();
        return $setting ? $setting->value : $default;
    }

    /**
     * 설정값 저장/업데이트
     */
    public static function set(string $key, mixed $value, ?int $updatedBy = null): static
    {
        return static::updateOrCreate(
            ['key' => $key],
            ['value' => (string) $value, 'updated_by' => $updatedBy]
        );
    }
}
