import { defineStore } from 'pinia';
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
