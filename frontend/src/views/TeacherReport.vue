<template>
  <div class="teacher-report-container">
    <el-card class="report-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>备课报告</span>
          <el-button @click="loadReport">刷新</el-button>
        </div>
      </template>

      <div v-if="report">
        <h3 style="margin: 0 0 8px">提醒消息中心</h3>
        <div class="alert-toolbar">
          <el-switch v-model="showIgnored" active-text="显示已忽略" inactive-text="隐藏已忽略" />
          <el-button link type="primary" @click="clearIgnored" v-if="ignoredKeys.length > 0">清空忽略记录</el-button>
        </div>
        <el-alert
          v-for="a in visibleAlerts"
          :key="a.alert_key"
          :title="a.title"
          :type="getAlertType(a.level)"
          :description="`${a.detail}｜建议：${a.action_hint}`"
          :closable="false"
          show-icon
          style="margin-bottom: 8px"
        >
          <template #default>
            <div class="alert-actions">
              <el-button size="small" type="primary" @click="handleAlertAction(a)">立即处理</el-button>
              <el-button size="small" @click="toggleIgnore(a.alert_key)">
                {{ isIgnored(a.alert_key) ? '恢复' : '忽略' }}
              </el-button>
            </div>
          </template>
        </el-alert>
        <el-empty v-if="visibleAlerts.length === 0" description="暂无提醒，当前教学节奏稳定" />

        <div class="stats-grid">
          <el-statistic title="平均成绩(%)" :value="report.student_score_overview.avg_score_pct || 0" />
          <el-statistic title="平均完成率" :value="Math.round((report.student_score_overview.avg_completion_rate || 0) * 100)">
            <template #suffix>%</template>
          </el-statistic>
          <el-statistic title="近7天对话次数" :value="report.usage_frequency.chat_count_7d || 0" />
          <el-statistic title="日均对话(7天)" :value="report.usage_frequency.avg_daily_chat_7d || 0" />
        </div>

        <h3 style="margin: 18px 0 8px">班级成绩与完成情况</h3>
        <el-table :data="report.classes" style="width: 100%">
          <el-table-column prop="class_name" label="班级" min-width="140" />
          <el-table-column prop="student_count" label="学生数" width="90" />
          <el-table-column prop="assignment_count" label="作业数" width="90" />
          <el-table-column prop="submission_count" label="提交数" width="90" />
          <el-table-column label="完成率" width="120">
            <template #default="{ row }">
              {{ Math.round((row.completion_rate || 0) * 100) }}%
            </template>
          </el-table-column>
          <el-table-column label="平均成绩" width="120">
            <template #default="{ row }">
              {{ row.avg_score_pct || 0 }}%
            </template>
          </el-table-column>
        </el-table>

        <h3 style="margin: 18px 0 8px">教师偏好标签</h3>
        <div class="tags-row">
          <el-tag v-for="tag in report.preference_tags" :key="tag" style="margin-right: 8px; margin-bottom: 8px">
            {{ tag }}
          </el-tag>
          <span v-if="!report.preference_tags || report.preference_tags.length === 0" class="empty-text">暂无偏好标签</span>
        </div>

        <h3 style="margin: 18px 0 8px">备课建议</h3>
        <el-alert
          v-for="(item, idx) in report.prep_recommendations"
          :key="idx"
          :title="item"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 8px"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { analysisApi } from '@/api/analysis'

const router = useRouter()
const loading = ref(false)
const report = ref(null)
const alerts = ref([])
const showIgnored = ref(false)
const ignoredKeys = ref([])

const visibleAlerts = computed(() => {
  if (showIgnored.value) return alerts.value
  const ignored = new Set(ignoredKeys.value)
  return alerts.value.filter(a => !ignored.has(a.alert_key))
})

const loadReport = async () => {
  loading.value = true
  try {
    const [reportRes, alertRes, ignoredRes] = await Promise.all([
      analysisApi.getTeachingReport(),
      analysisApi.getTeachingAlerts(),
      analysisApi.getIgnoredTeachingAlerts()
    ])
    report.value = reportRes
    alerts.value = alertRes || []
    ignoredKeys.value = ignoredRes || []
  } catch (error) {
    ElMessage.error('加载备课报告失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const getAlertType = (level) => {
  if (level === 'high') return 'error'
  if (level === 'medium') return 'warning'
  return 'info'
}

const isIgnored = (key) => ignoredKeys.value.includes(key)

const toggleIgnore = async (key) => {
  try {
    const nextIgnored = !isIgnored(key)
    await analysisApi.updateTeachingAlertState(key, nextIgnored)
    if (nextIgnored) {
      if (!ignoredKeys.value.includes(key)) ignoredKeys.value.push(key)
      ElMessage.success('已忽略该提醒')
    } else {
      ignoredKeys.value = ignoredKeys.value.filter(k => k !== key)
      ElMessage.success('已恢复该提醒')
    }
  } catch (error) {
    ElMessage.error('更新提醒状态失败：' + (error.response?.data?.detail || error.message))
  }
}

const clearIgnored = async () => {
  try {
    await analysisApi.clearIgnoredTeachingAlerts()
    ignoredKeys.value = []
    ElMessage.success('已清空忽略记录')
  } catch (error) {
    ElMessage.error('清空失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleAlertAction = (alert) => {
  if (alert.category === 'deadline') {
    router.push('/assignment-management')
    return
  }
  if (alert.category === 'class_completion') {
    router.push('/class-management')
    return
  }
  if (alert.category === 'student_risk' && alert.student_id) {
    router.push({ path: '/analysis', query: { sid: String(alert.student_id) } })
    return
  }
  router.push('/analysis')
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.teacher-report-container {
  height: 100%;
}

.report-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(140px, 1fr));
  gap: 16px;
  margin-bottom: 8px;
}

.tags-row {
  min-height: 32px;
}

.empty-text {
  color: #909399;
}

.alert-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.alert-actions {
  margin-top: 8px;
}
</style>
