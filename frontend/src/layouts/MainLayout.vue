<template>
  <div class="main-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>AI备课系统</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
          background-color="#ffffff"
          text-color="#333333"
          active-text-color="#409EFF"
        >
          <!-- 通用菜单（所有角色可见） -->
          <el-menu-item index="/chat">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI对话</span>
          </el-menu-item>
          
          <!-- 教师和管理员专用菜单 -->
          <template v-if="authStore.user?.role === 'teacher' || authStore.isAdmin">
            <el-menu-item index="/teaching-design">
              <el-icon><Document /></el-icon>
              <span>教学设计</span>
            </el-menu-item>
            <el-menu-item index="/multimedia">
              <el-icon><Picture /></el-icon>
              <span>多媒体资源</span>
            </el-menu-item>
            <el-menu-item index="/analysis">
              <el-icon><DataAnalysis /></el-icon>
              <span>学情分析</span>
            </el-menu-item>
            <el-menu-item index="/teacher-report">
              <el-icon><DataAnalysis /></el-icon>
              <span>备课报告</span>
            </el-menu-item>
            <el-menu-item index="/question-bank">
              <el-icon><Collection /></el-icon>
              <span>题库管理</span>
            </el-menu-item>
            <el-menu-item index="/ppt-management">
              <el-icon><Files /></el-icon>
              <span>PPT管理</span>
            </el-menu-item>
          </template>
          
          <!-- 教师专用菜单 -->
          <template v-if="authStore.user?.role === 'teacher'">
            <el-divider />
            <el-menu-item index="/class-management">
              <el-icon><School /></el-icon>
              <span>班级管理</span>
            </el-menu-item>
            <el-menu-item index="/assignment-management">
              <el-icon><Document /></el-icon>
              <span>作业管理</span>
            </el-menu-item>
          </template>
          
          <!-- 学生专用菜单 -->
          <template v-if="authStore.user?.role === 'student'">
            <el-menu-item index="/student-assignment">
              <el-icon><EditPen /></el-icon>
              <span>我的作业</span>
            </el-menu-item>
          </template>
          
          <!-- 管理员菜单 -->
          <template v-if="authStore.isAdmin">
            <el-divider />
            <el-menu-item index="/admin/users">
              <el-icon><Setting /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-header class="header">
          <div class="header-content">
            <div class="header-title">{{ currentTitle }}</div>
            <div class="header-right">
              <el-dropdown @command="handleCommand">
                <span class="user-info">
                  <el-icon><User /></el-icon>
                  {{ authStore.user?.username }}
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ChatDotRound, Document, Picture, DataAnalysis, User, ArrowDown, Collection, Files, Setting, School, EditPen } from '@element-plus/icons-vue'
import { ElDivider } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || 'AI辅助教师备课系统')

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.clearAuth()
    router.push('/login')
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background-color: #ffffff;
}

.sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  height: 100vh;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e4e7ed;
}

.logo h2 {
  font-size: 18px;
  color: #333333;
  font-weight: 500;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
}

.header {
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  height: 60px;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-title {
  font-size: 18px;
  font-weight: 500;
  color: #333333;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #333333;
  font-size: 14px;
}

.user-info .el-icon {
  margin: 0 5px;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>

