<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class ChatRoom extends Model
{
    protected $fillable = ['name','type','created_by'];

    public function users() {
        return $this->hasMany(ChatRoomUser::class);
    }

    public function messages() {
        return $this->hasMany(ChatMessage::class);
    }

    public function creator() {
        return $this->belongsTo(User::class, 'created_by');
    }
}
