<script setup lang="ts">
import { ref, shallowRef, computed, onMounted, onUnmounted, triggerRef } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskManager } from '@/composables/useTaskManager'
import { ApiClient } from '@/api'
import type { CommentExportTask } from '@/types/api'
import ConfirmModal from './ConfirmModal.vue'

const router = useRouter()
const taskManager = useTaskManager()

const {
  tasks,
  sortedTasks,
  isPolling,
  loadAllTasks,
  startPolling,
  stopPolling,
  downloadTaskFile,
  deleteTask
} = taskManager

const selectedTasks = ref<Set<string>>(new Set())
const loadingError = ref<string | null>(null)
const classifyingTasks = ref<Set<string>>(new Set())
const classifyProgress = ref<Record<string, number>>({})
const classificationStatus = ref<Record<string, 'none' | 'running' | 'completed' | 'failed'>>({})
const classificationPollIntervals = ref<Record<string, NodeJS.Timeout>>({})

// 弹框状态
const showErrorModal = ref(false)
const errorMessage = ref('')
const showConfirmModal = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmType = ref<'info' | 'success' | 'error' | 'warning'>('info')
const confirmCallback = ref<(() => void) | null>(null)
const pendingDeleteCount = ref(0)

onMounted(async () => {
  console.log('DownloadHistory mounted，开始加载任务...')
  console.log('API_BASE_URL:', import.meta.env.VITE_API_BASE_URL || '/api')
  try {
    loadingError.value = null
    await loadAllTasks()
    tasks.value.forEach(task => {
      if (task.classification_status === 'running') {
        classificationStatus.value[task.task_id] = 'running'
        classifyingTasks.value.add(task.task_id)
        classifyProgress.value[task.task_id] = task.classification_progress || 0
        pollClassificationStatus(task.task_id)
      }
    })
    console.log('任务已加载，开始轮询...')
    startPolling()
  } catch (err: any) {
    console.error('加载任务时出错:', err)
    loadingError.value = err.message || '加载失败，请检查网络连接'
  }
})

onUnmounted(() => {
  console.log('DownloadHistory unmounted，停止轮询')
  stopPolling()
  Object.values(classificationPollIntervals.value).forEach(intervalId => {
    clearInterval(intervalId)
  })
  classificationPollIntervals.value = {}
})

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '等待中',
    running: '进行中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: string) => {
  const classMap: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-700',
    running: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700'
  }
  return classMap[status] || 'bg-gray-100 text-gray-700'
}

const getStatusIcon = (status: string) => {
  if (status === 'completed') {
    return '✓'
  } else if (status === 'failed') {
    return '✗'
  } else if (status === 'running') {
    return '⟳'
  } else {
    return '⏱'
  }
}

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

const handleDownload = async (task: CommentExportTask) => {
  try {
    const filename = `${task.platform}_comments_${task.aweme_id}.csv`
    await downloadTaskFile(task.task_id, filename)
  } catch (err: any) {
    console.error('下载失败:', err)
    errorMessage.value = err.message || '下载失败'
    showErrorModal.value = true
  }
}

const handleDelete = async (taskId: string) => {
  confirmTitle.value = '确认删除'
  confirmMessage.value = '确定要删除这个任务吗？'
  confirmType.value = 'warning'
  confirmCallback.value = async () => {
    try {
      await deleteTask(taskId, true)
    } catch (err: any) {
      console.error('删除失败:', err)
      errorMessage.value = err.message || '删除失败'
      showErrorModal.value = true
    }
  }
  showConfirmModal.value = true
}

const toggleSelect = (taskId: string) => {
  if (selectedTasks.value.has(taskId)) {
    selectedTasks.value.delete(taskId)
  } else {
    selectedTasks.value.add(taskId)
  }
}

const handleBatchDelete = async () => {
  if (selectedTasks.value.size === 0) {
    return
  }

  pendingDeleteCount.value = selectedTasks.value.size
  confirmTitle.value = '确认批量删除'
  confirmMessage.value = `确定要删除选中的 ${selectedTasks.value.size} 个任务吗？`
  confirmType.value = 'warning'
  confirmCallback.value = async () => {
    for (const taskId of selectedTasks.value) {
      try {
        await deleteTask(taskId, true)
      } catch (err) {
        console.error('删除任务失败:', taskId, err)
      }
    }

    selectedTasks.value.clear()
    pendingDeleteCount.value = 0
    await loadAllTasks()
  }
  showConfirmModal.value = true
}

const handleClassify = async (task: CommentExportTask) => {
  if (classifyingTasks.value.has(task.task_id)) {
    return
  }

  try {
    classifyingTasks.value.add(task.task_id)
    classifyProgress.value[task.task_id] = 0
    classificationStatus.value[task.task_id] = 'running'

    await ApiClient.startClassify(task.task_id, 20, 5)

    pollClassificationStatus(task.task_id)
  } catch (err: any) {
    console.error('启动分类失败:', err)
    if (classificationPollIntervals.value[task.task_id]) {
      clearInterval(classificationPollIntervals.value[task.task_id])
      delete classificationPollIntervals.value[task.task_id]
    }
    classifyingTasks.value.delete(task.task_id)
    delete classifyProgress.value[task.task_id]
    delete classificationStatus.value[task.task_id]
    errorMessage.value = err.message || '启动分类失败'
    showErrorModal.value = true
  }
}

const pollClassificationStatus = async (taskId: string) => {
  if (classificationPollIntervals.value[taskId]) {
    return
  }
  const intervalId = setInterval(async () => {
    try {
      const status = await ApiClient.getClassifyStatus(taskId)
      if (classifyProgress.value[taskId] !== status.classification_progress) {
        classifyProgress.value[taskId] = status.classification_progress
      }
      classificationStatus.value[taskId] = status.classification_status

      if (status.classification_status === 'completed') {
        clearInterval(intervalId)
        delete classificationPollIntervals.value[taskId]
        classifyingTasks.value.delete(taskId)
        delete classifyProgress.value[taskId]
        delete classificationStatus.value[taskId]
        await loadAllTasks()
        const summaryText = status.classification_summary 
          ? Object.entries(status.classification_summary).map(([cat, count]) => `${cat}: ${count}`).join('\n')
          : '无'
        confirmTitle.value = '分类完成'
        confirmMessage.value = `分类完成！\n分类统计：\n${summaryText}`
        confirmType.value = 'success'
        confirmCallback.value = null
        showConfirmModal.value = true
      } else if (status.classification_status === 'failed') {
        clearInterval(intervalId)
        delete classificationPollIntervals.value[taskId]
        classifyingTasks.value.delete(taskId)
        delete classifyProgress.value[taskId]
        delete classificationStatus.value[taskId]
        errorMessage.value = status.error_message || '分类失败'
        showErrorModal.value = true
      }
    } catch (err) {
      console.error('查询分类状态失败:', err)
    }
  }, 5000)
  classificationPollIntervals.value[taskId] = intervalId
}

const handleDownloadClassified = async (task: CommentExportTask) => {
  try {
    const filename = `${task.platform}_comments_${task.aweme_id}_classified.csv`
    const blob = await ApiClient.downloadClassifiedFile(task.task_id)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (err: any) {
    console.error('下载分类文件失败:', err)
    errorMessage.value = err.message || '下载失败'
    showErrorModal.value = true
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <header class="mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
        <button
          @click="router.push('/')"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-lg font-medium shadow-sm hover:shadow-md hover:text-blue-600 transition-all duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          返回主页
        </button>
      </header>

      <!-- Main Content -->
      <main class="animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            导出记录
          </h1>
          <p class="text-gray-600">
            查看和管理您的评论导出任务
          </p>
        </div>

        <!-- Tasks List -->
        <div v-if="tasks.length > 0" class="space-y-4">
          <!-- Batch Actions -->
          <div v-if="selectedTasks.size > 0" class="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
            <span class="text-red-700">
              已选择 {{ selectedTasks.size }} 个任务
            </span>
            <button
              @click="handleBatchDelete"
              class="px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
            >
              批量删除
            </button>
          </div>

          <!-- Task Items -->
          <div
            v-for="task in sortedTasks"
            :key="task.task_id"
            class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="flex items-start gap-4">
              <!-- Checkbox -->
              <div class="flex-shrink-0 mt-1">
                <input
                  type="checkbox"
                  :checked="selectedTasks.has(task.task_id)"
                  @change="toggleSelect(task.task_id)"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
              </div>

              <!-- Task Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center gap-3">
                    <span
                      :class="[
                        'px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5',
                        getStatusClass(task.status)
                      ]"
                    >
                      {{ getStatusIcon(task.status) }} {{ getStatusText(task.status) }}
                    </span>
                    <span class="text-sm text-gray-500">
                      {{ task.platform === 'douyin' ? '抖音' : 'TikTok' }}
                    </span>
                    <span class="text-sm text-gray-700 font-medium">
                      {{ task.aweme_id }}
                    </span>
                    <span v-if="task.status === 'completed'" class="text-sm text-blue-600">
                      {{ task.total_fetched }} 条评论
                    </span>
                  </div>
                  <span class="text-sm text-gray-500">
                    {{ formatTime(task.created_at) }}
                  </span>
                </div>

                <!-- Progress -->
                <div v-if="task.status === 'running'" class="mb-3">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-sm text-gray-700">
                      已获取 {{ task.total_fetched }} / {{ task.max_comments }} 条评论
                    </span>
                    <span class="text-sm text-gray-700 font-medium">
                      {{ task.progress }}%
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${task.progress}%` }"
                    ></div>
                  </div>
                </div>

                <!-- Error Message -->
                <div v-if="task.status === 'failed' && task.error_message" class="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p class="text-sm text-red-700">
                    {{ task.error_message }}
                  </p>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2">
                  <button
                    v-if="task.status === 'completed'"
                    @click="handleDownload(task)"
                    class="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 transition-colors flex items-center gap-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                    </svg>
                    下载原始评论
                  </button>
                  <button
                    v-if="task.status === 'completed' && !classificationStatus[task.task_id]"
                    @click="handleClassify(task)"
                    class="px-4 py-2 bg-purple-500 text-white rounded-lg text-sm font-medium hover:bg-purple-600 transition-colors flex items-center gap-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                    AI评论分类
                  </button>
                  <button
                    v-if="classificationStatus[task.task_id] === 'running'"
                    disabled
                    class="px-4 py-2 bg-purple-300 text-white rounded-lg text-sm font-medium flex items-center gap-2 cursor-not-allowed"
                  >
                    <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    分类中... {{ classifyProgress[task.task_id] || task.classification_progress || 0 }}%
                  </button>
                  <div v-if="classificationStatus[task.task_id] === 'running'" class="w-full mt-2">
                    <div class="w-full bg-purple-200 rounded-full h-2">
                      <div
                        class="bg-purple-500 h-2 rounded-full transition-all duration-300"
                        :style="{ width: `${classifyProgress[task.task_id] || task.classification_progress || 0}%` }"
                      ></div>
                    </div>
                  </div>
                  <button
                    v-if="classificationStatus[task.task_id] === 'completed'"
                    @click="handleDownloadClassified(task)"
                    class="px-4 py-2 bg-indigo-500 text-white rounded-lg text-sm font-medium hover:bg-indigo-600 transition-colors flex items-center gap-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                    </svg>
                    下载已分类评论
                  </button>
                  <button
                    @click="handleDelete(task.task_id)"
                    class="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors flex items-center gap-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-if="loadingError" class="bg-red-50 border-2 border-red-200 rounded-xl p-8 shadow-sm text-center mb-6">
          <svg class="w-16 h-16 mx-auto mb-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <h3 class="text-lg font-medium text-red-900 mb-2">
            加载失败
          </h3>
          <p class="text-red-700 mb-4">
            {{ loadingError }}
          </p>
          <div class="flex gap-2 justify-center">
            <button
              @click="loadAllTasks().then(() => loadingError = null).catch(e => loadingError = e.message)"
              class="inline-flex items-center px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
            >
              重新加载
            </button>
            <button
              @click="router.push('/')"
              class="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-lg font-medium hover:bg-red-200 transition-colors"
            >
              返回主页
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="tasks.length === 0" class="bg-white border-2 border-gray-200 rounded-xl p-12 shadow-sm text-center">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            暂无下载任务
          </h3>
          <p class="text-gray-600 mb-4">
            开始导出评论后，任务将显示在这里
          </p>
          <button
            @click="router.push('/')"
            class="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
          >
            返回主页
          </button>
        </div>
      </main>
    </div>
  </div>

  <!-- 错误提示弹框 -->
  <ConfirmModal
    v-model:show="showErrorModal"
    type="error"
    :title="errorMessage ? '提示' : ''"
    :message="errorMessage"
    confirm-text="知道了"
  />

  <!-- 确认弹框 -->
  <ConfirmModal
    v-model:show="showConfirmModal"
    :type="confirmType"
    :title="confirmTitle"
    :message="confirmMessage"
    :show-cancel="!!confirmCallback"
    confirm-text="确定"
    cancel-text="取消"
    @confirm="confirmCallback && confirmCallback()"
  />
</template>
