<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCommentExporter } from '@/composables/useCommentExporter'

interface Props {
  platform: 'douyin' | 'tiktok'
}

const props = defineProps<Props>()
const router = useRouter()
const {
  isFetching,
  isExporting,
  exportProgress,
  error,
  exportDouyinComments,
  exportTiktokComments,
  downloadCSV,
  comments,
  totalComments,
  fetchDouyinComments,
  fetchTiktokComments,
  resetExporter,
  currentTaskId
} = useCommentExporter()

const exportType = ref<'id' | 'url'>('url')
const awemeId = ref('')
const url = ref('')
const maxComments = ref(100)
const hasFetched = ref(false)
const showErrorModal = ref(false)
const errorMessage = ref('')

const platformName = computed(() => {
  return props.platform === 'douyin' ? '抖音' : 'TikTok'
})

const displayedComments = computed(() => {
  return comments.value.slice(0, 5)
})

const handleFetch = async () => {
  const validationError = validateInput()

  if (validationError) {
    errorMessage.value = validationError
    showErrorModal.value = true
    return
  }

  try {
    resetExporter()
    hasFetched.value = false

    if (props.platform === 'douyin') {
      await fetchDouyinComments({
        aweme_id: exportType.value === 'id' ? awemeId.value.trim() : undefined,
        url: exportType.value === 'url' ? url.value.trim() : undefined,
        max_comments: maxComments.value
      })
    } else {
      await fetchTiktokComments({
        aweme_id: exportType.value === 'id' ? awemeId.value.trim() : undefined,
        url: exportType.value === 'url' ? url.value.trim() : undefined,
        max_comments: maxComments.value
      })
    }

    hasFetched.value = true
  } catch (err) {
    console.error('获取评论失败:', err)
    errorMessage.value = err.message || '未知错误'
    showErrorModal.value = true
  }
}

const handleExport = async () => {
  try {
    let blob: Blob

    if (props.platform === 'douyin') {
      blob = await exportDouyinComments({
        aweme_id: exportType.value === 'id' ? awemeId.value.trim() : undefined,
        url: exportType.value === 'url' ? url.value.trim() : undefined,
        max_comments: maxComments.value
      })
    } else {
      blob = await exportTiktokComments({
        aweme_id: exportType.value === 'id' ? awemeId.value.trim() : undefined,
        url: exportType.value === 'url' ? url.value.trim() : undefined,
        max_comments: maxComments.value
      })
    }

    const filename = `${props.platform}_comments_${Date.now()}.csv`
    downloadCSV(blob, filename)
  } catch (err) {
    console.error('导出评论失败:', err)
    errorMessage.value = err.message || '未知错误'
    showErrorModal.value = true
  }
}

const validateInput = (): string | null => {
  if (exportType.value === 'id') {
    if (!awemeId.value.trim()) {
      return '请输入视频ID'
    }
  } else {
    if (!url.value.trim()) {
      return '请输入视频URL'
    }
  }

  if (maxComments.value < 1 || maxComments.value > 10000) {
    return '导出数量必须在1-10000之间'
  }

  return null
}

const isInputValid = computed(() => {
  if (exportType.value === 'id') {
    return awemeId.value.trim().length > 0
  } else {
    return url.value.trim().length > 0
  }
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const closeErrorModal = () => {
  showErrorModal.value = false
  errorMessage.value = ''
}

const goToHistory = () => {
  router.push('/download-history')
}
</script>

<template>
  <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600">
        <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
        </svg>
      </div>
      <h2 class="text-xl font-bold text-gray-900">
        导出{{ platformName }}视频评论
      </h2>
    </div>

    <div class="mb-6">
      <div class="flex gap-3">
        <button
          @click="exportType = 'url'"
          :class="{
            'px-5 py-2.5 rounded-lg font-medium transition-all duration-200': true,
            'bg-gradient-to-r from-blue-500 to-blue-600 text-white': exportType === 'url',
            'bg-gray-100 text-gray-700 hover:bg-gray-200': exportType !== 'url'
          }"
        >
          通过URL导出
        </button>

        <button
          @click="exportType = 'id'"
          :class="{
            'px-5 py-2.5 rounded-lg font-medium transition-all duration-200': true,
            'bg-gradient-to-r from-blue-500 to-blue-600 text-white': exportType === 'id',
            'bg-gray-100 text-gray-700 hover:bg-gray-200': exportType !== 'id'
          }"
        >
          通过ID导出
        </button>
      </div>
    </div>

    <div class="space-y-4 mb-6">
      <div v-if="exportType === 'id'">
        <label class="block text-gray-900 font-medium mb-2">
          视频ID
        </label>
        <input
          v-model="awemeId"
          type="text"
          placeholder="请输入视频ID，例如: 7372484719365098803"
          class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          :disabled="isFetching || isExporting"
        />
      </div>

      <div v-else>
        <label class="block text-gray-900 font-medium mb-2">
          视频URL
        </label>
        <textarea
          v-model="url"
          placeholder="请将抖音分享链接粘贴于此，一次一条&#10;https://www.douyin.com/video/75840010001000010001"
          class="w-full h-24 px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
          :disabled="isFetching || isExporting"
        />
      </div>

      <div>
        <label class="block text-gray-900 font-medium mb-2">
          最大导出数量 (1-10000)
        </label>
        <input
          v-model.number="maxComments"
          type="number"
          min="1"
          max="10000"
          placeholder="100"
          class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          :disabled="isFetching || isExporting"
        />
      </div>
    </div>

    <div class="flex gap-3 mb-6">
      <button
        @click="handleFetch"
        :disabled="isFetching || isExporting || !isInputValid || hasFetched"
        class="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isFetching ? '获取中...' : '获取评论' }}
      </button>

      <button
        v-if="hasFetched && !currentTaskId"
        @click="handleExport"
        :disabled="isExporting"
        class="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isExporting ? '创建任务中...' : '导出CSV' }}
      </button>

      <button
        v-if="currentTaskId"
        @click="goToHistory"
        class="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg font-medium hover:from-purple-600 hover:to-purple-700 transition-all duration-200"
      >
        查看下载任务
      </button>
    </div>

    <div v-if="isFetching" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex items-center gap-3 text-blue-700">
        <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>正在获取{{ platformName }}评论数据...</span>
      </div>
    </div>

    <div v-if="hasFetched && comments.length > 0" class="mt-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">
          评论预览 (显示前5条，共获取{{ totalComments }}条)
        </h3>
      </div>

      <div class="space-y-3">
        <div
          v-for="(comment, index) in displayedComments"
          :key="comment.comment_id"
          class="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white font-medium">
              {{ comment.user_nickname.charAt(0) }}
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-gray-900">{{ comment.user_nickname }}</span>
                <div class="flex items-center gap-3 text-sm text-gray-500">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                    </svg>
                    <span>{{ comment.digg_count }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                    <span>{{ comment.reply_count }}</span>
                  </div>
                </div>
              </div>

              <p class="text-gray-700 text-sm mb-2 break-words">
                {{ comment.text }}
              </p>

              <div class="flex items-center gap-3 text-xs text-gray-500">
                <span>{{ formatDate(comment.create_time) }}</span>
                <span v-if="comment.ip_label">·{{ comment.ip_label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="totalComments > 5" class="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg text-center">
        <span class="text-gray-600 text-sm">
          还有 <span class="font-medium text-gray-900">{{ totalComments - 5 }}</span> 条评论未显示，请导出CSV文件查看完整数据
        </span>
      </div>
    </div>

    <div v-if="!isExporting && !error && exportProgress > 0" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-center gap-3 text-green-700">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <span>
          导出成功！已完成 {{ maxComments }} 条评论的导出
        </span>
      </div>
    </div>
  </div>

  <!-- 错误弹框 -->
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div
      v-if="showErrorModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="closeErrorModal"
    >
      <!-- 背景遮罩 -->
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>

      <!-- 弹框内容 -->
      <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 transform transition-all">
        <!-- 关闭按钮 -->
        <button
          @click="closeErrorModal"
          class="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>

        <!-- 错误图标 -->
        <div class="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
          <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>

        <!-- 错误消息 -->
        <h3 class="text-lg font-semibold text-gray-900 text-center mb-2">
          提示
        </h3>
        <p class="text-gray-600 text-center mb-6">
          {{ errorMessage }}
        </p>

        <!-- 确认按钮 -->
        <button
          @click="closeErrorModal"
          class="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200"
        >
          知道了
        </button>
      </div>
    </div>
  </Transition>
</template>
