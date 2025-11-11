// import { createRouter, createWebHistory } from 'vue-router'
// import Login1View from '@/views/Login1View.vue'
// import DashboardView from '@/views/DashboardView.vue'
// import RegisterView  from   '@/views/RegisterView.vue'



// const routes = [
//   {
//     path: '/',
//     redirect: '/login'
//   },
//   {
//     path: '/login',
//     name: 'Login',
//     component: Login1View
//   },
//   // {
//   //   path: '/dashboard',
//   //   name: 'Dashboard',
//   //   component: DashboardView
//   // },
  
//   {
//     path: '/manager/dashboard',
//     name: 'Dashboard',
//     component: DashboardView
//   },
  
//   // {
//   //   path: '/client/dashboard',  
//   //   name: 'Dashboard',
//   //   component: DashboardView
//   // },
//   {
//     path: '/register',
//     name:'register',
//     component: RegisterView,
//     meta: { requiresGuest: true }

//   }
// ]

// const router = createRouter({
//   history: createWebHistory(),
//   routes
// })

// export default router
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
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/manager',
    component: () => import('@/layouts/ManagerLayout.vue'),
    meta: { requiresAuth: true, role: 'manager' },
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
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/manager/dashboard')
  } else if (to.meta.role && authStore.user?.role !== to.meta.role) {
    next('/login')
  } else {
    next()
  }
})

export default router