<script setup lang="ts">
import { ref } from 'vue'
import { useVideoParser } from '@/composables/useVideoParser'
import { useConfigStore } from '@/stores/config'
import { extractUrls } from '@/utils/url'

const { isProcessing, error, parseMultipleUrls, progress, results, resetParser } = useVideoParser()
const configStore = useConfigStore()

const inputText = ref('')
const downloadingUrls = ref<Set<string>>(new Set())
const showErrorModal = ref(false)
const errorMessage = ref('')

const validateInput = (text: string): string | null => {
  const urls = extractUrls(text)

  if (urls.length === 0) {
    return '没有检测到有效的链接，请检查输入的内容是否正确。'
  }

  if (urls.length > configStore.maxTakeUrls) {
    return `输入的链接太多啦，一次只能输入${configStore.maxTakeUrls}个链接，请减少后再试！`
  }

  return null
}

const handleParse = async () => {
  const validationError = validateInput(inputText.value)

  if (validationError) {
    errorMessage.value = validationError
    showErrorModal.value = true
    return
  }

  const urls = extractUrls(inputText.value).slice(0, configStore.maxTakeUrls)

  try {
    await parseMultipleUrls(urls, false)
  } catch (err) {
    console.error('批量解析失败:', err)
  }
}

const handleReset = () => {
  inputText.value = ''
  resetParser()
}

const closeErrorModal = () => {
  showErrorModal.value = false
  errorMessage.value = ''
}

const downloadVideo = async (resultItem: any, type: 'nwm' | 'wm') => {
  // 使用URL和类型作为唯一标识
  const key = `${resultItem.url}_${type}`

  if (downloadingUrls.value.has(key)) {
    return
  }

  // 设置下载状态
  downloadingUrls.value.add(key)

  try {
    // 使用后端下载API，传递原始URL（不是视频URL）
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
    
    // 传递原始URL（用户输入的链接），后端会解析这个URL
    const originalUrl = resultItem.url
    const withWatermark = type === 'wm'
    
    // 构建下载URL
    const downloadUrl = `${apiBaseUrl}/download?url=${encodeURIComponent(originalUrl)}&prefix=true&with_watermark=${withWatermark}`

    // 使用fetch发起请求，等待服务端完成后再恢复按钮状态
    const response = await fetch(downloadUrl)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || '下载失败')
    }

    // 获取文件名从响应头
    const contentDisposition = response.headers.get('content-disposition')
    let filename = getVideoFilename(resultItem, type)
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match) {
        filename = match[1].replace(/['"]/g, '')
      }
    }

    // 创建下载链接
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

  } catch (err: any) {
    console.error('下载失败:', err)
    errorMessage.value = `下载失败：${err.message || '未知错误'}`
    showErrorModal.value = true
  } finally {
    // 无论成功或失败，都恢复按钮状态
    downloadingUrls.value.delete(key)
  }
}

const getVideoFilename = (result: any, type: 'nwm' | 'wm') => {
  const prefix = type === 'nwm' ? '无水印_' : '有水印_'
  const safeDesc = result.data.desc.replace(/[^\w\u4e00-\u9fa5]/g, '_').slice(0, 50)
  const videoId = result.data.video_id || 'video'
  return `${prefix}${videoId}_${safeDesc}.mp4`
}
</script>

<template>
  <div class="space-y-6">
    <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md">
      <div class="mb-6 space-y-4">
        <label class="block text-gray-900 font-medium mb-2">
          请直接粘贴多个(最多{{ configStore.maxTakeUrls }}个)链接，无需使用符号分开
        </label>
        
        <textarea
          v-model="inputText"
          placeholder="请输入视频链接，支持抖音、TikTok、Bilibili&#10;可一次输入多个链接，无需使用符号分开&#10;https://v.douyin.com/L4FJNR3/&#10;https://www.tiktok.com/@username/video/7156033831819037994&#10;https://www.bilibili.com/video/BV1M1421t7hT&#10;"
          class="w-full h-32 px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
          :disabled="isProcessing"
        />

        <div class="flex items-center justify-between flex-wrap gap-4">
          <div class="flex items-center gap-2 text-gray-600 text-sm">
            
          </div>

          <div class="flex gap-3">
            <button
              @click="handleReset"
              :disabled="isProcessing"
              class="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              重置
            </button>
            <button
              @click="handleParse"
              :disabled="isProcessing || !inputText.trim()"
              class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isProcessing ? '解析中...' : '开始解析' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="isProcessing" class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center gap-3 text-blue-700">
          <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <div>
            正在解析 ({{ progress.completed }}/{{ progress.total }})
            <span v-if="progress.currentUrl" class="ml-2 text-sm text-blue-600 block mt-1">
              {{ progress.currentUrl }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center gap-3 text-red-700">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>{{ error }}</span>
        </div>
      </div>

      <div v-if="progress.total > 0 && !isProcessing" class="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h3 class="font-bold text-lg mb-3 text-gray-900">解析结果</h3>
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-green-600">{{ progress.success }}</div>
            <div class="text-sm text-gray-600">成功</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-red-600">{{ progress.failed }}</div>
            <div class="text-sm text-gray-600">失败</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-blue-600">{{ progress.total }}</div>
            <div class="text-sm text-gray-600">总计</div>
          </div>
        </div>
      </div>
    </div>

    <div class="space-y-4">
      <div
        v-for="result in results"
        :key="result.id"
        class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md transition-all duration-200"
      >
        <div class="flex items-center gap-3 mb-4">
          <div
            :class="{
              'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0': true,
              'bg-green-500': result.status === 'success',
              'bg-red-500': result.status === 'failed',
              'bg-yellow-500': result.status === 'parsing',
              'bg-gray-400': result.status === 'idle'
            }"
          >
            <svg v-if="result.status === 'success'" class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <svg v-else-if="result.status === 'failed'" class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <svg v-else class="animate-spin w-6 h-6 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-900 break-all font-medium">{{ result.url }}</div>
          </div>
        </div>

        <div v-if="result.status === 'success' && result.data" class="space-y-4">
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="flex flex-col">
              <span class="text-gray-500 mb-1">类型</span>
              <span class="text-gray-900 font-medium">{{ result.data.type === 'video' ? '视频' : '图集' }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-gray-500 mb-1">平台</span>
              <span class="text-gray-900 font-medium">{{ result.data.platform }}</span>
            </div>
            <div class="col-span-2 flex flex-col">
              <span class="text-gray-500 mb-1">描述</span>
              <span class="text-gray-900 font-medium">{{ result.data.desc }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-gray-500 mb-1">作者</span>
              <span class="text-gray-900 font-medium">{{ result.data.author.nickname }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-gray-500 mb-1">作者ID</span>
              <span class="text-gray-900 font-medium">{{ result.data.author.unique_id }}</span>
            </div>
          </div>

          <div v-if="result.data.type === 'video'" class="space-y-3">
            <div class="text-sm font-semibold text-gray-900">下载视频</div>
              <div class="flex flex-wrap gap-2">
               <button
                 @click="downloadVideo(result, 'nwm')"
                 :disabled="downloadingUrls.has(`${result.url}_nwm`) || !result.data.video_data?.nwm_video_url_HQ"
                 class="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
               >
                 <svg v-if="downloadingUrls.has(`${result.url}_nwm`)" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                   <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                   <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                 </svg>
                 <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                 </svg>
                 {{ downloadingUrls.has(`${result.url}_nwm`) ? '下载中...' : '下载无水印(高清)' }}
               </button>
               <button
                 @click="downloadVideo(result, 'wm')"
                 :disabled="downloadingUrls.has(`${result.url}_wm`) || !result.data.video_data?.wm_video_url_HQ"
                 class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
               >
                 <svg v-if="downloadingUrls.has(`${result.url}_wm`)" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                   <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                   <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                 </svg>
                 <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                 </svg>
                 {{ downloadingUrls.has(`${result.url}_wm`) ? '下载中...' : '下载有水印(高清)' }}
               </button>
              </div>
            </div>

          <div v-else-if="result.data.type === 'image'" class="space-y-3">
            <div class="text-sm font-semibold text-gray-900">图片预览</div>
            <div class="grid grid-cols-3 gap-3">
              <img
                v-for="(url, index) in result.data.image_data?.no_watermark_image_list"
                :key="index"
                :src="url"
                alt="图片"
                class="w-full h-32 object-cover rounded-lg hover:scale-105 transition-transform duration-200"
              />
            </div>
          </div>
        </div>

        <div v-else-if="result.status === 'failed'" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="text-red-700 text-sm font-medium">
            {{ result.error || '解析失败' }}
          </div>
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
  </div>
</template>
