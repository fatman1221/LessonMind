import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/chat',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/chat',
        name: 'Chat',
        component: () => import('@/views/Chat.vue'),
        meta: { title: 'AI对话' }
      },
      {
        path: '/teaching-design',
        name: 'TeachingDesign',
        component: () => import('@/views/TeachingDesign.vue'),
        meta: { title: '教学设计' }
      },
      {
        path: '/multimedia',
        name: 'Multimedia',
        component: () => import('@/views/Multimedia.vue'),
        meta: { title: '多媒体资源' }
      },
      {
        path: '/analysis',
        name: 'Analysis',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: '学情分析' }
      },
      {
        path: '/question-bank',
        name: 'QuestionBank',
        component: () => import('@/views/QuestionBank.vue'),
        meta: { title: '题库管理' }
      },
      {
        path: '/ppt-management',
        name: 'PPTManagement',
        component: () => import('@/views/PPTManagement.vue'),
        meta: { title: 'PPT管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } 
  // 如果已登录，访问登录页则跳转到首页
  else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/chat')
  } 
  // 其他情况正常跳转
  else {
    next()
  }
})

export default router

