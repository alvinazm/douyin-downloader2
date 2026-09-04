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

interface InsReelResult {
  url: string
  username: string | null
  items: InsReelItem[]
  warning?: string | null
}

interface InsParseResult {
  // 单数模式（向后兼容）
  username?: string
  items?: InsReelItem[]
  warning?: string | null
  // urls 模式
  results?: InsReelResult[]
}

const result = ref<InsParseResult | null>(null)
const downloadingUrls = ref<Set<string>>(new Set())

const PLACEHOLDER_MULTI = `https://www.instagram.com/leonmbz/reels/
https://www.instagram.com/alivn.azm/reels/
https://www.instagram.com/yapayzekaserisi/reels/`

/**
 * 视频发布"新鲜度"阈值（分钟）
 * 距离当前时间 < FRESH_MINUTES 分钟时，UI 显示 🆕 高亮角标
 * 测试时可临时改成 90 等其他值
 */
const FRESH_MINUTES = 30

const validateInput = (text: string): string | null => {
  const urls = parseUrls(text)
  if (urls.length === 0) {
    return '请输入至少一个作者 reels 链接'
  }
  for (const u of urls) {
    if (!/instagram\.com\/.+\/reels?\/?(\?.*)?$/i.test(u)) {
      return `链接格式错误：${u}\n应为 https://www.instagram.com/<username>/reels/`
    }
  }
  return null
}

/**
 * 从输入框提取有效 URL（一行一个，或空格 / 逗号分隔）
 */
const parseUrls = (text: string): string[] => {
  return text
    .split(/[\n\r\s,]+/)
    .map(u => u.trim())
    .filter(u => u.length > 0)
}

/**
 * 判断视频是否"刚发布"（< 30 分钟）
 * 返回 { isFresh, label, minutes }
 *  - isFresh: true/false
 *  - label: 用于 UI 显示的本地化字符串（'刚刚发布' / 'X 分钟前' / ''）
 *  - minutes: 距离当前时间的分钟数（无 timestamp 时为 null）
 */
const freshnessInfo = (timestamp?: number | null): { isFresh: boolean; label: string; minutes: number | null } => {
  if (!timestamp || typeof timestamp !== 'number') {
    return { isFresh: false, label: '', minutes: null }
  }
  // timestamp 是 Unix 秒
  const minutes = Math.floor((Date.now() / 1000 - timestamp) / 60)
  if (minutes < 0) {
    // 时间在未来（罕见，可能是时区差异），当作刚发布
    return { isFresh: true, label: '🆕 刚刚发布', minutes: 0 }
  }
  if (minutes < 1) {
    return { isFresh: true, label: '🆕 刚刚发布', minutes: 0 }
  }
  if (minutes < FRESH_MINUTES) {
    return { isFresh: true, label: `🆕 ${minutes} 分钟前发布`, minutes }
  }
  return { isFresh: false, label: '', minutes }
}

const fetchLatest = async () => {
  errorMessage.value = ''
  const err = validateInput(inputUrl.value)
  if (err) {
    errorMessage.value = err
    showErrorModal.value = true
    return
  }

  const urls = parseUrls(inputUrl.value)
  if (urls.length === 0) {
    errorMessage.value = '请输入至少一个有效的作者 reels 链接'
    showErrorModal.value = true
    return
  }

  loading.value = true
  result.value = null
  try {
    // 多个 URL 走 urls 数组；单个走 url 单数（向后兼容）
    const data = await ApiClient.insCreatorLatest({
      url: urls.length === 1 ? urls[0] : undefined,
      urls: urls.length > 1 ? urls : undefined,
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

        <textarea
          v-model="inputUrl"
          rows="4"
          :placeholder="PLACEHOLDER_MULTI"
          class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all duration-200 font-mono text-sm resize-y"
          :disabled="loading"
          @keydown.ctrl.enter="fetchLatest"
          @keydown.meta.enter="fetchLatest"
        />

        <div class="flex items-center justify-between flex-wrap gap-4">
          <div class="text-xs text-gray-500">
            <p>说明：</p>
            <ul class="list-disc ml-4 mt-1 space-y-0.5">
              <li>支持一次输入多个作者链接（换行、空格、逗号分隔）</li>
              <li>每个作者返回最近 <b>2 条</b>视频（按发布时间倒序）</li>
              <li>需要在系统 Chrome 中登录过 Instagram（用于 yt-dlp 读取 cookie）</li>
              <li>多作者并发抓取，预计 5-15 秒/作者</li>
              <li>Mac 按 <kbd class="px-1 bg-gray-100 border border-gray-300 rounded">⌘</kbd>+<kbd class="px-1 bg-gray-100 border border-gray-300 rounded">Enter</kbd> 触发，Win/Linux 用 <kbd class="px-1 bg-gray-100 border border-gray-300 rounded">Ctrl</kbd>+<kbd class="px-1 bg-gray-100 border border-gray-300 rounded">Enter</kbd></li>
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
      <!-- 单数模式（向后兼容） -->
      <template v-if="!result.results">
        <div v-if="result.warning" class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg text-sm">
          ⚠️ {{ result.warning }}
        </div>

        <div v-if="result.items && result.items.length === 0 && !result.warning" class="text-center text-gray-500 py-12">
          未抓取到任何视频，请检查链接或 Chrome 登录态
        </div>

        <div
          v-for="(item, idx) in (result.items || [])"
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
              <span class="font-medium text-gray-900">@{{ item.uploader || result.username || '未知作者' }}</span>
              <span class="text-gray-300">·</span>
              <span class="font-medium text-pink-600" :title="item.timestamp ? '发布时间（UTC+8）' : ''">
                📅 发布于 {{ item.formatted_publish_time || item.upload_date || '未知时间' }}
              </span>
              <span
                v-if="freshnessInfo(item.timestamp).isFresh"
                class="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 border border-green-300 rounded-full text-xs font-medium animate-pulse"
                :title="`距今 ${freshnessInfo(item.timestamp).minutes} 分钟`"
              >
                {{ freshnessInfo(item.timestamp).label }}
              </span>
              <span v-if="item.upload_date && item.formatted_publish_time" class="text-xs text-gray-400">
                ({{ item.upload_date }})
              </span>
            </div>

            <!-- 描述 -->
            <div v-if="item.description" class="text-gray-700 text-sm mb-2 line-clamp-3 break-all">
              {{ item.description }}
            </div>

            <!-- 缩略图：限制最大宽度 320px，IG reel 竖屏 9:16 -->
            <a v-if="item.thumbnail" :href="item.url" target="_blank" class="block mb-3">
              <img
                :src="item.thumbnail"
                class="w-full max-w-xs max-h-80 object-cover rounded-lg border border-gray-200"
                style="aspect-ratio: 9 / 16;"
                loading="lazy"
              />
            </a>

            <!-- 数据统计 -->
            <div class="flex items-center gap-4 text-xs text-gray-500 mb-3 flex-wrap">
              <span v-if="item.like_count != null">❤️ {{ item.like_count.toLocaleString() }}</span>
              <span v-if="item.comment_count != null">💬 {{ item.comment_count.toLocaleString() }}</span>
              <span v-if="item.view_count != null">▶️ {{ item.view_count.toLocaleString() }}</span>
              <span v-if="item.duration != null" title="视频时长">⏱️ 时长 {{ item.duration.toFixed(2) }}s</span>
            </div>

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
      </template>

      <!-- urls 模式：按作者分组展示 -->
      <template v-else>
        <div v-if="!result.results || result.results.length === 0" class="text-center text-gray-500 py-12">
          未抓取到任何作者，请检查链接或 Chrome 登录态
        </div>

        <div
          v-for="(group, gIdx) in (result.results || [])"
          :key="group.url || gIdx"
          class="bg-white border-2 border-gray-200 rounded-xl p-5 shadow-md space-y-4"
        >
          <!-- 作者组头部 -->
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-gray-100 pb-3">
            <div class="flex items-center gap-2">
              <div class="w-9 h-9 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 text-white flex items-center justify-center font-bold">
                {{ gIdx + 1 }}
              </div>
              <div>
                <div class="text-base font-semibold text-gray-900">
                  @{{ group.username || '未知作者' }}
                </div>
                <a
                  :href="group.url"
                  target="_blank"
                  class="text-xs text-blue-500 hover:underline break-all"
                >
                  {{ group.url }}
                </a>
              </div>
            </div>
            <span
              v-if="group.warning"
              class="text-xs text-yellow-700 bg-yellow-50 border border-yellow-200 px-2 py-1 rounded"
            >
              ⚠️ {{ group.warning }}
            </span>
            <span
              v-else-if="group.items.length === 0"
              class="text-xs text-gray-500 bg-gray-50 border border-gray-200 px-2 py-1 rounded"
            >
              无数据
            </span>
            <span
              v-else
              class="text-xs text-green-700 bg-green-50 border border-green-200 px-2 py-1 rounded"
            >
              ✓ {{ group.items.length }} 条
            </span>
          </div>

          <!-- 该作者的 2 条视频 -->
          <div
            v-for="(item, idx) in group.items"
            :key="item.shortcode"
            class="flex items-start gap-3 pl-2"
          >
            <div class="flex-shrink-0 w-6 h-6 rounded-full bg-pink-100 text-pink-600 flex items-center justify-center text-xs font-bold">
              {{ idx + 1 }}
            </div>

            <div class="flex-1 min-w-0">
              <!-- 头部：发布时间 -->
              <div class="flex items-center gap-2 text-sm text-gray-700 mb-1 flex-wrap">
                <span class="font-medium text-pink-600" :title="item.timestamp ? '发布时间（UTC+8）' : ''">
                  📅 发布于 {{ item.formatted_publish_time || item.upload_date || '未知时间' }}
                </span>
                <span
                  v-if="freshnessInfo(item.timestamp).isFresh"
                  class="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 border border-green-300 rounded-full text-xs font-medium animate-pulse"
                  :title="`距今 ${freshnessInfo(item.timestamp).minutes} 分钟`"
                >
                  {{ freshnessInfo(item.timestamp).label }}
                </span>
                <span v-if="item.upload_date && item.formatted_publish_time" class="text-xs text-gray-400">
                  ({{ item.upload_date }})
                </span>
                <span v-if="item.uploader && item.uploader !== group.username" class="text-xs text-gray-500">
                  by @{{ item.uploader }}
                </span>
              </div>

              <!-- 描述 -->
              <div v-if="item.description" class="text-gray-700 text-xs mb-2 line-clamp-2 break-all">
                {{ item.description }}
              </div>

              <!-- 缩略图 + 数据 同行 -->
              <div class="flex gap-3">
                <a v-if="item.thumbnail" :href="item.url" target="_blank" class="flex-shrink-0">
                  <img
                    :src="item.thumbnail"
                    class="w-20 max-h-28 object-cover rounded border border-gray-200"
                    style="aspect-ratio: 9 / 16;"
                    loading="lazy"
                  />
                </a>

                <div class="flex-1 min-w-0 space-y-1">
                  <div class="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
                    <span v-if="item.like_count != null">❤️ {{ item.like_count.toLocaleString() }}</span>
                    <span v-if="item.comment_count != null">💬 {{ item.comment_count.toLocaleString() }}</span>
                    <span v-if="item.view_count != null">▶️ {{ item.view_count.toLocaleString() }}</span>
                    <span v-if="item.duration != null" title="视频时长">⏱️ {{ item.duration.toFixed(2) }}s</span>
                  </div>

                  <button
                    @click="downloadReel(item)"
                    :disabled="downloadingUrls.has(item.url)"
                    class="px-3 py-1.5 bg-green-500 text-white rounded text-xs font-medium hover:bg-green-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                  >
                    <svg v-if="downloadingUrls.has(item.url)" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                    </svg>
                    {{ downloadingUrls.has(item.url) ? '下载中' : '下载' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
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
