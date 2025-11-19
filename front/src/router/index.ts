import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

import ComplaintForm from '@/views/ComplaintForm.vue'
import ComplaintStatus from '@/views/ComplaintStatus.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignUpView from '@/views/SignUpView.vue'

// Lazy load
const ComplaintStatusDetail = () => import('@/views/ComplaintStatusDetail.vue')
const NotFoundView = () => import('@/views/NotFoundView.vue')
const StaffDashboardView = () => import('@/views/StaffDashboardView.vue')
const PolicyView = () => import('@/views/PolicyView.vue')
const UserProfileView = () => import('@/views/UserProfileView.vue')

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: HomeView },

  // Auth routes
  { path: '/auth/login', name: 'login', component: LoginView },
  { path: '/auth/signup', name: 'signup', component: SignUpView },
  { path: '/auth/profile', name: 'profile', component: UserProfileView },

  // Complaint routes
  { path: '/comp/form', name: 'form', component: ComplaintForm },
  { path: '/comp/status', name: 'status', component: ComplaintStatus },
  { path: '/comp/status/:id', name: 'status-detail', component: ComplaintStatusDetail, props: true },

  // Staff routes
  { path: '/staff', name: 'staff', component: StaffDashboardView },

  // Info routes
  { path: '/policy', name: 'policy', component: PolicyView },

  // 404
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
