// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login1View.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/manager',
    component: () => import('@/layouts/ManagerLayout.vue'),
    meta: { requiresAuth: true, managerPortal: true },
    children: [
      {
        path: 'dashboard',
        name: 'ManagerDashboard',
        component: () => import('@/views/manager/DashboardView.vue')
      },
      {
        path: 'contacts',
        name: 'ManagerContacts',
        component: () => import('@/views/manager/ContactsView.vue')
      },
      {
        path: 'contacts/:id',
        name: 'ContactDetail',
        component: () => import('@/views/manager/ContactDetailView.vue')
      },
      {
        path: 'deals',
        name: 'ManagerDeals',
        component: () => import('@/views/manager/DealsView.vue')
      },
      {
        path: 'deals-kanban',
        name: 'ManagerDealsKanban',
        component: () => import('@/views/manager/DealsKanbanView.vue')
      },
      {
        path: 'deals/new',
        name: 'NewDeal',
        component: () => import('@/views/manager/DealFormView.vue')
      },
      {
        path: 'deals/:id',
        name: 'DealDetail',
        component: () => import('@/views/manager/DealDetailView.vue')
      },
      {
        path: 'services',
        name: 'ManagerServices',
        component: () => import('@/views/manager/ServicesView.vue')
      },
      {
        path: 'calendar',
        name: 'ManagerCalendar',
        component: () => import('@/views/manager/CalendarView.vue')
      },
      {
        path: 'analytics',
        name: 'ManagerAnalytics',
        component: () => import('@/views/manager/AnalyticsView.vue')
      },
      {
        path: 'marketing',
        name: 'ManagerMarketing',
        component: () => import('@/views/manager/MarketingView.vue')
      },
      {
        path: 'documents',
        name: 'ManagerDocuments',
        component: () => import('@/views/manager/DocumentsView.vue')
      },
      {
        path: 'chats',
        name: 'ManagerChats',
        component: () => import('@/views/manager/ChatsView.vue')
      },
      {
        path: 'emails',
        name: 'ManagerEmails',
        component: () => import('@/views/manager/EmailsView.vue')
      },
      {
        path: 'applications',
        name: 'ManagerApplications',
        component: () => import('@/views/manager/Applications.vue')
      },
      {
        path: 'profile',
        name: 'ManagerProfile',
        component: () => import('@/views/manager/ProfileView.vue')
      },
      {
        path: 'users',
        name: 'ManagerUsers',
        component: () => import('@/views/manager/UsersTeamView.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Навигационный guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore() //Получает доступ к хранилищу Pinia/Vuex, где хранятся данные о пользователе (авторизован ли он, его роль и т.д.)

// Если маршрут требует авторизацию и пользователь не авторизован, перенаправляем на страницу входа 
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/manager/dashboard')
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/manager/dashboard')
  } else if (to.meta.managerPortal) {
    const r = authStore.user?.role
    if (r === 'manager' || r === 'admin') next()
    else next('/login')
  } else {
    next()
  }
})

export default router