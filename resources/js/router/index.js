import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
    // 홈
    { path: '/', component: () => import('../pages/Home.vue'), name: 'home' },

    // 인증
    { path: '/auth/register', component: () => import('../pages/auth/Register.vue'), name: 'register', meta: { guest: true } },
    { path: '/auth/login',    component: () => import('../pages/auth/Login.vue'),    name: 'login',    meta: { guest: true } },

    // 커뮤니티
    { path: '/community',          component: () => import('../pages/community/BoardList.vue'),  name: 'boards' },
    { path: '/community/:slug',    component: () => import('../pages/community/PostList.vue'),   name: 'post-list' },
    { path: '/community/post/:id', component: () => import('../pages/community/PostDetail.vue'), name: 'post-detail' },
    { path: '/community/write',    component: () => import('../pages/community/PostWrite.vue'),  name: 'post-write', meta: { auth: true } },

    // 구인구직
    { path: '/jobs',         component: () => import('../pages/jobs/JobList.vue'),   name: 'jobs' },
    { path: '/jobs/:id',     component: () => import('../pages/jobs/JobDetail.vue'), name: 'job-detail' },
    { path: '/jobs/write',   component: () => import('../pages/jobs/JobWrite.vue'),  name: 'job-write', meta: { auth: true } },

    // 중고장터
    { path: '/market',        component: () => import('../pages/market/MarketList.vue'),   name: 'market' },
    { path: '/market/:id',    component: () => import('../pages/market/MarketDetail.vue'), name: 'market-detail' },
    { path: '/market/write',  component: () => import('../pages/market/MarketWrite.vue'),  name: 'market-write', meta: { auth: true } },

    // 업소록
    { path: '/directory',      component: () => import('../pages/directory/BusinessList.vue'),   name: 'directory' },
    { path: '/directory/:id',  component: () => import('../pages/directory/BusinessDetail.vue'), name: 'business-detail' },
    { path: '/directory/register', component: () => import('../pages/directory/BusinessRegister.vue'), name: 'business-register', meta: { auth: true } },

    // 포인트
    { path: '/points', component: () => import('../pages/points/PointDashboard.vue'), name: 'points', meta: { auth: true } },

    // 메시지
    { path: '/messages', component: () => import('../pages/messages/MessageInbox.vue'), name: 'messages', meta: { auth: true } },

    // 프로필
    { path: '/profile/:username', component: () => import('../pages/profile/UserProfile.vue'), name: 'profile' },

    // 관리자
    { path: '/admin', component: () => import('../pages/admin/Dashboard.vue'), name: 'admin', meta: { auth: true, admin: true } },

    // 404
    { path: '/:pathMatch(.*)*', component: () => import('../pages/NotFound.vue'), name: 'not-found' },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
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
});

export default router;
