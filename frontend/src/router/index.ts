import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import StudentLogin from '../components/StudentLogin.vue';
import TeacherLogin from '../components/TeacherLogin.vue';
import StudentSignup from '../components/StudentSignup.vue';
import TeacherSignup from '../components/TeacherSignup.vue';
import Game from '../components/game/Game.vue';
import TeacherDashboard from '../components/dashboard/TeacherDashboard.vue';

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
    {
      path: '/teacher/dashboard',
      component: TeacherDashboard,
      meta: { requiresAuth: true, requiresTeacher: true }
    }
  ]
});

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  if (to.meta.requiresAuth && !authStore.user) {
    next('/');
  } else if (to.meta.requiresTeacher && authStore.user?.role !== 'teacher') {
    next('/');
  } else {
    next();
  }
});

export default router;