import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import StudentLogin from '../components/StudentLogin.vue';
import TeacherLogin from '../components/TeacherLogin.vue';
import StudentSignup from '../components/StudentSignup.vue';
import TeacherSignup from '../components/TeacherSignup.vue';
import Game from '../components/game/Game.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/student/login', component: StudentLogin },
    { path: '/teacher/login', component: TeacherLogin },
    { path: '/student/signup', component: StudentSignup },
    { path: '/teacher/signup', component: TeacherSignup },
    { 
      path: '/game',
      component: Game,
      meta: { requiresAuth: true }
    },
  ]
});

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  if (to.meta.requiresAuth && !authStore.user) {
    next('/');
  } else {
    next();
  }
});

export default router;