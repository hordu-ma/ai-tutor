import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        // Lazy-load the component for better performance
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'upload',
        name: 'HomeworkUpload',
        component: () => import('@/views/HomeworkUploadView.vue'),
        meta: { title: '作业上传' },
      },

      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/HistoryView.vue'),
        meta: { title: '批改历史' },
      },
      {
        path: 'ai-chat',
        name: 'AiChat',
        component: () => import('@/views/AiChatView.vue'),
        meta: { title: 'AI智能辅导' },
      },
      {
        path: 'student-management',
        name: 'StudentManagement',
        component: () => import('@/views/StudentManagementView.vue'),
        meta: { title: '学生管理' },
      },
      {
        path: 'error-trends',
        name: 'ErrorTrends',
        component: () => import('@/views/ErrorTrendsView.vue'),
        meta: { title: '错误趋势分析' },
      },
      {
        path: 'multi-subject-summary',
        name: 'MultiSubjectSummary',
        component: () => import('@/views/MultiSubjectSummaryView.vue'),
        meta: { title: '多科目汇总分析' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
