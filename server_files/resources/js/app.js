import './bootstrap';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useAuthStore } from './stores/auth';
import { useSiteStore } from './stores/site';
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

// 앱 시작 시 관리자 공개 설정 로드 (메뉴 on/off, 사이트명 등)
const siteStore = useSiteStore();
siteStore.load();

// After login token updates, refresh Echo auth header
router.afterEach(() => {
    const token = localStorage.getItem('sk_token');
    if (window.Echo && token) {
        window.Echo.options.auth.headers.Authorization = `Bearer ${token}`;
    }
});

app.mount('#app');

// 빌드 후 옛날 청크 파일(404)을 요청할 때 자동 새로고침
// Vite 빌드마다 파일명 해시가 바뀌는데 브라우저가 옛날 app.js를 캐시한 경우 발생
router.onError((err) => {
    const isChunkLoadError =
        err?.message?.includes('Failed to fetch dynamically imported module') ||
        err?.message?.includes('Loading chunk') ||
        err?.message?.includes('Importing a module script failed') ||
        err?.name === 'ChunkLoadError';
    if (isChunkLoadError) {
        // 이미 새로고침 시도한 경우 무한루프 방지
        const lastReload = sessionStorage.getItem('_chunk_reload');
        const now = Date.now();
        if (!lastReload || now - Number(lastReload) > 10000) {
            sessionStorage.setItem('_chunk_reload', String(now));
            window.location.reload();
        }
    }
});
