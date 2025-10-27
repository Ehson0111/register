import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import RegisterView  from   '@/views/RegisterView.vue'



const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView
  },
  {
    path: '/register',
    name:'register',
    component: RegisterView,
    meta: { requiresGuest: true }

  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router