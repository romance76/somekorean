import paramiko

def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=10)
    return ssh

def read_remote(path):
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    with sftp.file(path, 'r') as f:
        content = f.read().decode('utf-8')
    sftp.close()
    ssh.close()
    return content

def write_remote(path, content):
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    with sftp.file(path, 'w') as f:
        f.write(content)
    sftp.close()
    ssh.close()
    print(f"Written: {path}")

# ===== 1. Patch ElderHome.vue =====
print("Patching ElderHome.vue...")
vue = read_remote('/var/www/somekorean/resources/js/pages/elder/ElderHome.vue')

# Add import for usePushNotification after the CallModal import
old_import = "import CallModal from '../../components/CallModal.vue'"
new_import = """import CallModal from '../../components/CallModal.vue'
import { usePushNotification } from '../../composables/usePushNotification'"""

if 'usePushNotification' not in vue:
    vue = vue.replace(old_import, new_import)

    # Add push notification setup after auth store
    old_auth = "const auth = useAuthStore()"
    new_auth = """const auth = useAuthStore()
const { subscribe: pushSubscribe, requestPermission } = usePushNotification()"""
    vue = vue.replace(old_auth, new_auth)

    # Add push subscription in onMounted, after loadCheckinHistory()
    old_mounted = """  loadSettings()
  loadCheckinHistory()

  // Socket connection + WebRTC setup"""
    new_mounted = """  loadSettings()
  loadCheckinHistory()

  // 푸시 알림 구독
  requestPermission().then(perm => {
    if (perm === 'granted' && auth.user?.id) {
      pushSubscribe(auth.user.id)
    }
  })

  // Socket connection + WebRTC setup"""
    vue = vue.replace(old_mounted, new_mounted)

    write_remote('/var/www/somekorean/resources/js/pages/elder/ElderHome.vue', vue)
    print("ElderHome.vue patched!")
else:
    print("ElderHome.vue already has push notification code, skipping.")

# ===== 2. Patch ElderController.php =====
print("\nPatching ElderController.php...")
php = read_remote('/var/www/somekorean/app/Http/Controllers/API/ElderController.php')

if 'send-notification' not in php:
    # Find the SOS method's return statement and add push notification code before it
    old_sos_return = """            $guardianPhone = $settings->guardian_phone;
            $guardianName  = $settings->guardian_name ?? '보호자';

            return response()->json([
                'message'       => 'SOS 신호가 발송되었습니다.',
                'sos_id'        => $sosLog->id,
                'guardian_name' => $guardianName,
                'sent_to'       => $guardianPhone
                    ? substr($guardianPhone, 0, 3) . '****' . substr($guardianPhone, -4)
                    : null,
            ]);"""

    new_sos_return = """            // 보호자에게 소켓/푸시 알림
            if ($settings->guardian_user_id) {
                try {
                    \\Illuminate\\Support\\Facades\\Http::post('http://127.0.0.1:3001/send-notification', [
                        'userId' => (string) $settings->guardian_user_id,
                        'event' => 'elder:sos-alert',
                        'data' => [
                            'title' => '\\xF0\\x9F\\x9A\\xA8 긴급 SOS',
                            'message' => ($user->nickname ?? $user->name) . '님이 SOS를 발동했습니다!',
                            'body' => ($user->nickname ?? $user->name) . '님이 SOS를 발동했습니다!',
                            'url' => '/elder/guardian',
                            'elderId' => $user->id,
                            'elderName' => $user->nickname ?? $user->name,
                            'lat' => $request->input('lat'),
                            'lng' => $request->input('lng'),
                        ]
                    ]);
                } catch (\\Exception $e) {
                    \\Log::error('SOS push notification failed: ' . $e->getMessage());
                }
            }

            $guardianPhone = $settings->guardian_phone;
            $guardianName  = $settings->guardian_name ?? '보호자';

            return response()->json([
                'message'       => 'SOS 신호가 발송되었습니다.',
                'sos_id'        => $sosLog->id,
                'guardian_name' => $guardianName,
                'sent_to'       => $guardianPhone
                    ? substr($guardianPhone, 0, 3) . '****' . substr($guardianPhone, -4)
                    : null,
            ]);"""

    php = php.replace(old_sos_return, new_sos_return)
    write_remote('/var/www/somekorean/app/Http/Controllers/API/ElderController.php', php)
    print("ElderController.php patched!")
else:
    print("ElderController.php already has push notification code, skipping.")

# ===== 3. Check nginx config =====
print("\nChecking nginx config...")
nginx = read_remote('/etc/nginx/sites-enabled/somekorean')
if '/api/socket/' in nginx:
    print("Nginx already has /api/socket/ proxy - push-subscribe will work via /api/socket/push-subscribe")
else:
    print("WARNING: Nginx needs /api/socket/ proxy added!")

print("\nAll patches complete!")
