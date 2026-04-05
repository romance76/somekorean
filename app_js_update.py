import paramiko, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=20)
sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-600:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-200:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

# app.js 내용을 직접 서버에 씀
app_js = r"""import './bootstrap';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useAuthStore } from './stores/auth';
import Echo from 'laravel-echo';
import Pusher from 'pusher-js';

window.Pusher = Pusher;

window.Echo = new Echo({
    broadcaster: 'reverb',
    key: import.meta.env.VITE_REVERB_APP_KEY,
    wsHost: import.meta.env.VITE_REVERB_HOST,
    wsPort: import.meta.env.VITE_REVERB_PORT ?? 80,
    wssPort: import.meta.env.VITE_REVERB_PORT ?? 443,
    forceTLS: (import.meta.env.VITE_REVERB_SCHEME ?? 'https') === 'https',
    enabledTransports: ['ws', 'wss'],
    authEndpoint: '/broadcasting/auth',
    auth: {
        headers: {
            Authorization: `Bearer ${localStorage.getItem('sk_token') ?? ''}`,
        },
    },
});

const pinia = createPinia();
const app = createApp(App);
app.use(pinia);
app.use(router);

const authStore = useAuthStore();
authStore.initialize();

// 앱 시작 시 서버에서 최신 user 정보 갱신 (is_admin 등 캐시 문제 방지)
if (authStore.token) {
    authStore.fetchMe();
}

// After login token updates, refresh Echo auth header
router.afterEach(() => {
    const token = localStorage.getItem('sk_token');
    if (window.Echo && token) {
        window.Echo.options.auth.headers.Authorization = `Bearer ${token}`;
    }
});

app.mount('#app');
"""

with sftp.file(f'{APP}/resources/js/app.js', 'w') as f:
    f.write(app_js)
sys.stdout.buffer.write(b'app.js written\n')
sys.stdout.buffer.flush()

sftp.close()

run(f'cd {APP} && npm run build 2>&1 | tail -5', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -2')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

client.close()
sys.stdout.buffer.write(b'\n=== Done ===\n')
sys.stdout.buffer.flush()
