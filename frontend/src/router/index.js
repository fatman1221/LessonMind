import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

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
        meta: { title: '教学设计', requiresTeacher: true }
      },
      {
        path: '/multimedia',
        name: 'Multimedia',
        component: () => import('@/views/Multimedia.vue'),
        meta: { title: '多媒体资源', requiresTeacher: true }
      },
      {
        path: '/analysis',
        name: 'Analysis',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: '学情分析', requiresTeacher: true }
      },
      {
        path: '/teacher-report',
        name: 'TeacherReport',
        component: () => import('@/views/TeacherReport.vue'),
        meta: { title: '备课报告', requiresTeacher: true }
      },
      {
        path: '/question-bank',
        name: 'QuestionBank',
        component: () => import('@/views/QuestionBank.vue'),
        meta: { title: '题库管理', requiresTeacher: true }
      },
      {
        path: '/ppt-management',
        name: 'PPTManagement',
        component: () => import('@/views/PPTManagement.vue'),
        meta: { title: 'PPT管理', requiresTeacher: true }
      },
      {
        path: '/admin/users',
        name: 'AdminUserManagement',
        component: () => import('@/views/AdminUserManagement.vue'),
        meta: { title: '用户管理', requiresAdmin: true }
      },
      {
        path: '/class-management',
        name: 'ClassManagement',
        component: () => import('@/views/ClassManagement.vue'),
        meta: { title: '班级管理', requiresTeacher: true }
      },
      {
        path: '/assignment-management',
        name: 'AssignmentManagement',
        component: () => import('@/views/AssignmentManagement.vue'),
        meta: { title: '作业管理', requiresTeacher: true }
      },
      {
        path: '/student-assignment',
        name: 'StudentAssignment',
        component: () => import('@/views/StudentAssignment.vue'),
        meta: { title: '我的作业', requiresStudent: true }
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
    return
  }
  
  // 如果未登录，除了登录页其他都跳转到登录页
  if (!authStore.isAuthenticated && to.path !== '/login') {
    next('/login')
    return
  }
  
  // 如果已登录，访问登录页则跳转到首页
  if (to.path === '/login' && authStore.isAuthenticated) {
    // 根据角色跳转到不同首页
    if (authStore.user?.role === 'student') {
      next('/student-assignment')
    } else {
      next('/chat')
    }
    return
  }
  
  // 检查权限控制
  const userRole = authStore.user?.role
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    ElMessage.warning('需要管理员权限')
    // 根据角色跳转到对应首页
    if (userRole === 'student') {
      next('/student-assignment')
    } else {
      next('/chat')
    }
    return
  }
  
  // 检查是否需要教师权限（管理员也拥有教师权限）
  if (to.meta.requiresTeacher && userRole !== 'teacher' && !authStore.isAdmin) {
    ElMessage.warning('需要教师权限')
    // 根据角色跳转到对应首页
    if (userRole === 'student') {
      next('/student-assignment')
    } else {
      next('/chat')
    }
    return
  }
  
  // 检查是否需要学生权限
  if (to.meta.requiresStudent && userRole !== 'student') {
    ElMessage.warning('需要学生权限')
    next('/chat')
    return
  }
  
  // 其他情况正常跳转
  next()
})

export default router

