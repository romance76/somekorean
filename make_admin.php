<?php
require '/var/www/somekorean/vendor/autoload.php';
$app = require_once '/var/www/somekorean/bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

use App\Models\User;
use Illuminate\Support\Facades\Hash;

// romance76@gmail.com 을 admin으로 승격
$user = User::where('email', 'romance76@gmail.com')->first();
if ($user) {
    $user->update(['is_admin' => true, 'status' => 'active']);
    echo 'PROMOTED: ' . $user->email . PHP_EOL;
}

// admin@somekorean.com 생성 또는 업데이트
$admin = User::where('email', 'admin@somekorean.com')->first();
if ($admin) {
    $admin->update([
        'password' => Hash::make('Admin1234!'),
        'is_admin' => true,
        'status'   => 'active',
    ]);
    echo 'UPDATED: ' . $admin->email . PHP_EOL;
} else {
    $cols = ['name', 'username', 'email', 'password', 'is_admin', 'status'];
    $data = [
        'name'     => 'SomeKorean Admin',
        'username' => 'admin',
        'email'    => 'admin@somekorean.com',
        'password' => Hash::make('Admin1234!'),
        'is_admin' => true,
        'status'   => 'active',
    ];
    // 컬럼 존재 여부 체크 후 생성
    $fillable = (new User)->getFillable();
    $filtered = array_intersect_key($data, array_flip($fillable));
    $newAdmin = User::create($filtered);
    echo 'CREATED: ' . $newAdmin->email . PHP_EOL;
}
echo 'DONE' . PHP_EOL;
