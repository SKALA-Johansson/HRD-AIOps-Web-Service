import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import { useTutorDockStore } from '@/store/tutorDock.js'

const HR_STAFF = ['HR']

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/common/LandingView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/common/LoginView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('@/views/common/SignupView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/employee/ProfileView.vue'),
    meta: { requiresAuth: true, roles: ['EMPLOYEE', 'HR'] }
  },
  {
    path: '/learning',
    name: 'LearningHome',
    component: () => import('@/views/employee/LearningHomeView.vue'),
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] }
  },
  {
    path: '/learning/progress',
    name: 'LearningProgress',
    component: () => import('@/views/employee/LearningProgressView.vue'),
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] }
  },
  {
    path: '/learning/modules/:moduleId',
    name: 'LearningModule',
    component: () => import('@/views/employee/LearningModuleView.vue'),
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] }
  },
  {
    path: '/goals',
    name: 'Goals',
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] },
    beforeEnter() {
      return { name: 'LearningHome', replace: true }
    },
    component: () => import('@/views/common/EmptyRouteView.vue')
  },
  {
    path: '/curriculums/:curriculumId',
    name: 'CurriculumDetail',
    component: () => import('@/views/employee/CurriculumDetailView.vue'),
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] }
  },
  {
    path: '/tutor',
    name: 'Tutor',
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] },
    beforeEnter(to, from) {
      const dock = useTutorDockStore()
      dock.open()
      if (from.matched.length && from.path !== '/tutor') {
        return { path: from.fullPath, replace: true }
      }
      return { name: 'LearningHome', replace: true }
    },
    component: () => import('@/views/common/EmptyRouteView.vue')
  },
  {
    path: '/reports/me',
    name: 'MyReport',
    component: () => import('@/views/employee/MyReportView.vue'),
    meta: { requiresAuth: true, roles: ['EMPLOYEE'] }
  },
  {
    path: '/hr/dashboard',
    name: 'HrDashboard',
    component: () => import('@/views/hr/HrDashboardView.vue'),
    meta: { requiresAuth: true, roles: HR_STAFF }
  },
  {
    path: '/hr/goals',
    redirect: '/hr/curriculums'
  },
  {
    path: '/hr/approvals',
    redirect: '/hr/curriculums'
  },
  {
    path: '/hr/curriculums',
    name: 'HrCurriculums',
    component: () => import('@/views/hr/HrApprovalsView.vue'),
    meta: { requiresAuth: true, roles: HR_STAFF }
  },
  {
    path: '/hr/contents',
    name: 'HrContents',
    component: () => import('@/views/hr/HrContentListView.vue'),
    meta: { requiresAuth: true, roles: ['HR'] }
  },
  {
    path: '/hr/contents/new',
    name: 'HrContentNew',
    component: () => import('@/views/hr/HrContentFormView.vue'),
    meta: { requiresAuth: true, roles: ['HR'] }
  },
  {
    path: '/hr/contents/:contentId/edit',
    name: 'HrContentEdit',
    component: () => import('@/views/hr/HrContentFormView.vue'),
    meta: { requiresAuth: true, roles: ['HR'] }
  },
  {
    path: '/hr/reports',
    name: 'HrReports',
    component: () => import('@/views/hr/HrReportsView.vue'),
    meta: { requiresAuth: true, roles: HR_STAFF }
  },
  {
    path: '/hr/mentor/team-progress',
    redirect: '/hr/team-progress'
  },
  {
    path: '/hr/mentor/tutor-guide',
    redirect: '/hr/tutor-guide'
  },
  {
    path: '/hr/team-progress',
    name: 'HrTeamProgress',
    component: () => import('@/views/hr/MentorTeamProgressView.vue'),
    meta: { requiresAuth: true, roles: HR_STAFF }
  },
  {
    path: '/hr/tutor-guide',
    name: 'HrTutorGuide',
    component: () => import('@/views/hr/MentorTutorGuideView.vue'),
    meta: { requiresAuth: true, roles: HR_STAFF }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    if (auth.role === 'HR') return { name: 'HrDashboard' }
    return { name: 'LearningHome' }
  }
  if (to.meta.roles?.length) {
    const r = auth.role
    if (!r || !to.meta.roles.includes(r)) {
      return { name: 'Landing' }
    }
  }
})

export default router
