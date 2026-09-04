<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useConfigStore } from '@/stores/config'
import { ApiClient } from '@/api'

const router = useRouter()
const configStore = useConfigStore()

const inputUrl = ref('')
const loading = ref(false)
const errorMessage = ref('')
const showErrorModal = ref(false)

interface InsReelItem {
  shortcode: string
  url: string
  title?: string | null
  description?: string | null
  uploader?: string | null
  uploader_id?: string | null
  timestamp?: number | null
  upload_date?: string | null
  formatted_publish_time?: string | null
  duration?: number | null
  view_count?: number | null
  like_count?: number | null
  comment_count?: number | null
  thumbnail?: string | null
}

interface InsParseResult {
  username: string
  items: InsReelItem[]
  warning?: string | null
}

const result = ref<InsParseResult | null>(null)
const downloadingUrls = ref<Set<string>>(new Set())

const PLACEHOLDER = 'https://www.instagram.com/leonmbz/reels/'

const validateInput = (text: string): string | null => {
  const t = text.trim()
  if (!t) return '请输入作者 reels 链接'
  if (!/instagram\.com\/.+\/reels?\/?(\?.*)?$/i.test(t)) {
    return '链接格式应为 https://www.instagram.com/<username>/reels/'
  }
  return null
}

const fetchLatest = async () => {
  errorMessage.value = ''
  const err = validateInput(inputUrl.value)
  if (err) {
    errorMessage.value = err
    showErrorModal.value = true
    return
  }

  loading.value = true
  result.value = null
  try {
    const data = await ApiClient.insCreatorLatest({
      url: inputUrl.value.trim(),
      n: 2,
      list_limit: 20,
    })
    result.value = data as InsParseResult
  } catch (e: any) {
    console.error('ins 抓取失败:', e)
    errorMessage.value = `抓取失败：${e?.response?.data?.detail?.message || e?.message || '未知错误'}`
    showErrorModal.value = true
  } finally {
    loading.value = false
  }
}

const downloadReel = async (item: InsReelItem) => {
  const key = item.url
  if (downloadingUrls.value.has(key)) return
  downloadingUrls.value.add(key)

  try {
    const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string) || '/api'
    const downloadUrl = `${apiBaseUrl}/download?url=${encodeURIComponent(item.url)}&prefix=true&with_watermark=false`
    const response = await fetch(downloadUrl)
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || '下载失败')
    }

    const contentDisposition = response.headers.get('content-disposition')
    let filename = `instagram_${item.shortcode}.mp4`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match) filename = match[1].replace(/['"]/g, '')
    }

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
  } catch (e: any) {
    console.error('下载失败:', e)
    errorMessage.value = `下载失败：${e?.message || '未知错误'}`
    showErrorModal.value = true
  } finally {
    downloadingUrls.value.delete(key)
  }
}

const closeErrorModal = () => {
  showErrorModal.value = false
  errorMessage.value = ''
}
</script>

<template>
  <div class="space-y-6">
    <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md">
      <div class="mb-6 space-y-4">
        <label class="block text-gray-900 font-medium mb-2">
          请输入作者 <code class="px-1 bg-gray-100 rounded text-pink-600">/reels/</code> 链接
        </label>

        <input
          v-model="inputUrl"
          :placeholder="PLACEHOLDER"
          class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all duration-200"
          :disabled="loading"
          @keydown.enter="fetchLatest"
        />

        <div class="flex items-center justify-between flex-wrap gap-4">
          <div class="text-xs text-gray-500">
            <p>说明：</p>
            <ul class="list-disc ml-4 mt-1 space-y-0.5">
              <li>需要在系统 Chrome 中登录过 Instagram（用于 yt-dlp 读取 cookie）</li>
              <li>返回该作者最近 <b>2 条</b>视频（按发布时间倒序）</li>
            </ul>
          </div>
          <div class="flex gap-2">
            <button
              @click="router.push('/')"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-all duration-200"
            >
              返回首页
            </button>
            <button
              @click="fetchLatest"
              :disabled="loading || !inputUrl.trim()"
              class="px-5 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg font-medium hover:from-pink-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" fill-rule="evenodd" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? '抓取中...' : '获取最新视频' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="result" class="space-y-4">
      <div v-if="result.warning" class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg text-sm">
        ⚠️ {{ result.warning }}
      </div>

      <div v-if="result.items.length === 0 && !result.warning" class="text-center text-gray-500 py-12">
        未抓取到任何视频，请检查链接或 Chrome 登录态
      </div>

      <div
        v-for="(item, idx) in result.items"
        :key="item.shortcode"
        class="bg-white border-2 border-gray-200 rounded-xl p-5 shadow-md hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 text-white flex items-center justify-center font-bold text-sm">
            {{ idx + 1 }}
          </div>

          <div class="flex-1 min-w-0">
            <!-- 头部：作者 + 发布时间 -->
            <div class="flex items-center gap-2 text-sm text-gray-700 mb-1 flex-wrap">
              <span class="font-medium text-gray-900">@{{ item.uploader || result.username }}</span>
              <span class="text-gray-300">·</span>
              <span class="font-medium text-pink-600" :title="item.timestamp ? '发布时间（UTC+8）' : ''">
                📅 发布于 {{ item.formatted_publish_time || item.upload_date || '未知时间' }}
              </span>
              <span v-if="item.upload_date && item.formatted_publish_time" class="text-xs text-gray-400">
                ({{ item.upload_date }})
              </span>
            </div>

            <!-- 描述 -->
            <div v-if="item.description" class="text-gray-700 text-sm mb-2 line-clamp-3 break-all">
              {{ item.description }}
            </div>

            <!-- 缩略图 -->
            <a v-if="item.thumbnail" :href="item.url" target="_blank" class="block mb-3">
              <img
                :src="item.thumbnail"
                class="w-full max-h-64 object-cover rounded-lg border border-gray-200"
                loading="lazy"
              />
            </a>

            <!-- 数据统计 -->
            <div class="flex items-center gap-4 text-xs text-gray-500 mb-3 flex-wrap">
              <span v-if="item.like_count != null">❤️ {{ item.like_count.toLocaleString() }}</span>
              <span v-if="item.comment_count != null">💬 {{ item.comment_count.toLocaleString() }}</span>
              <span v-if="item.view_count != null">▶️ {{ item.view_count.toLocaleString() }}</span>
              <span v-if="item.duration != null" title="视频时长">⏱️ 时长 {{ item.duration }}s</span>
            </div>

            <!-- URL -->
            <a :href="item.url" target="_blank" class="text-xs text-blue-500 hover:underline break-all block mb-3">
              {{ item.url }}
            </a>

            <!-- 下载按钮 -->
            <button
              @click="downloadReel(item)"
              :disabled="downloadingUrls.has(item.url)"
              class="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="downloadingUrls.has(item.url)" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
              {{ downloadingUrls.has(item.url) ? '下载中...' : '下载视频' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误弹窗 -->
    <Teleport to="body">
      <div v-if="showErrorModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeErrorModal">
        <div class="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">提示</h3>
          <p class="text-gray-700 text-sm mb-4 whitespace-pre-wrap">{{ errorMessage }}</p>
          <button @click="closeErrorModal" class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-all duration-200">确定</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>
