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

# ── 1. auth store: initPromise 추가 ─────────────────────────────────────
auth_store = r"""import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useAuthStore = defineStore('auth', () => {
    const user  = ref(null);
    const token = ref(null);

    // 앱 초기화 완료 여부 (fetchMe 포함)
    let _resolveInit;
    const initPromise = new Promise(resolve => { _resolveInit = resolve; });

    const isLoggedIn = computed(() => !!token.value);

    function initialize() {
        const savedToken = localStorage.getItem('sk_token');
        const savedUser  = localStorage.getItem('sk_user');
        if (savedToken && savedUser) {
            token.value = savedToken;
            try { user.value = JSON.parse(savedUser); } catch {}
        }
    }

    async function login(email, password) {
        const { data } = await axios.post('/api/auth/login', { email, password });
        setAuth(data.token, data.user);
        return data;
    }

    async function register(form) {
        const { data } = await axios.post('/api/auth/register', form);
        setAuth(data.token, data.user);
        return data;
    }

    async function logout() {
        try { await axios.post('/api/auth/logout'); } catch {}
        clearAuth();
    }

    async function fetchMe() {
        try {
            const { data } = await axios.get('/api/auth/me');
            user.value = data.user;
            localStorage.setItem('sk_user', JSON.stringify(data.user));
        } catch {
            clearAuth();
        } finally {
            _resolveInit();
        }
    }

    // 토큰 없으면 즉시 resolve
    function resolveInit() { _resolveInit(); }

    function setAuth(tok, usr) {
        token.value = tok;
        user.value  = usr;
        localStorage.setItem('sk_token', tok);
        localStorage.setItem('sk_user', JSON.stringify(usr));
    }

    function clearAuth() {
        token.value = null;
        user.value  = null;
        localStorage.removeItem('sk_token');
        localStorage.removeItem('sk_user');
    }

    return { user, token, isLoggedIn, initPromise, initialize, login, register, logout, fetchMe, resolveInit };
});
"""

# ── 2. router/index.js: beforeEach async + await initPromise ────────────
router_guard = r"""router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();

    // 초기 fetchMe 완료 대기 (is_admin 캐시 race condition 방지)
    await authStore.initPromise;

    if (to.meta.auth && !authStore.isLoggedIn) {
        return next({ name: 'login', query: { redirect: to.fullPath } });
    }
    if (to.meta.admin && !authStore.user?.is_admin) {
        return next({ name: 'home' });
    }
    if (to.meta.guest && authStore.isLoggedIn) {
        return next({ name: 'home' });
    }
    next();
});"""

# ── 3. app.js: fetchMe 없으면 즉시 resolveInit ──────────────────────────
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

// 토큰 있으면 서버에서 최신 user 정보 가져옴 (is_admin 갱신)
// 없으면 즉시 initPromise resolve → router guard가 대기하지 않음
if (authStore.token) {
    authStore.fetchMe();
} else {
    authStore.resolveInit();
}

router.afterEach(() => {
    const token = localStorage.getItem('sk_token');
    if (window.Echo && token) {
        window.Echo.options.auth.headers.Authorization = `Bearer ${token}`;
    }
});

app.mount('#app');
"""

# 파일 쓰기
with sftp.file(f'{APP}/resources/js/stores/auth.js', 'w') as f:
    f.write(auth_store)
sys.stdout.buffer.write(b'auth.js written\n')

# router/index.js: 기존 beforeEach 부분만 교체
_, o, _ = client.exec_command(f'cat {APP}/resources/js/router/index.js', timeout=10)
router_content = o.read().decode('utf-8')

# beforeEach 블록 교체
import re
new_router = re.sub(
    r'router\.beforeEach\(.*?\}\);',
    router_guard,
    router_content,
    flags=re.DOTALL
)
with sftp.file(f'{APP}/resources/js/router/index.js', 'w') as f:
    f.write(new_router)
sys.stdout.buffer.write(b'router/index.js written\n')

with sftp.file(f'{APP}/resources/js/app.js', 'w') as f:
    f.write(app_js)
sys.stdout.buffer.write(b'app.js written\n')
sys.stdout.buffer.flush()

sftp.close()

run(f'cd {APP} && npm run build 2>&1 | tail -6', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -2')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

client.close()
sys.stdout.buffer.write(b'\n=== Done ===\n')
sys.stdout.buffer.flush()
