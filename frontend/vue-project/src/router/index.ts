import { createRouter, createWebHistory } from 'vue-router'
import Login1View from '@/views/Login1View.vue'
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
    component: Login1View
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView
  },
  
  {
    path: '/manager/dashboard',
    name: 'Dashboard',
    component: DashboardView
  },
  
  {
    path: '/client/dashboard',
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