import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { VideoResultItem, ParseProgress, ParseStatus } from '@/types/video'
import type { VideoData } from '@/types/api'
import { mockDouyinVideo, mockTikTokVideo, mockBilibiliVideo } from '@/assets/mock-data/videos'

/**
 * 解析器状态管理
 */
export const useParserStore = defineStore('parser', () => {
  // 状态
  const results = ref<VideoResultItem[]>([])
  const isParsing = ref(false)
  const currentUrlIndex = ref(0)

  // 计算属性
  const progress = computed<ParseProgress>(() => ({
    total: results.value.length,
    completed: results.value.filter(r => r.status !== 'parsing').length,
    success: results.value.filter(r => r.status === 'success').length,
    failed: results.value.filter(r => r.status === 'failed').length,
    currentUrl: isParsing.value ? results.value[currentUrlIndex.value]?.url : undefined
  }))

  const uniqueResults = computed(() => {
    const map = new Map<string, VideoResultItem>()
    results.value.forEach(item => {
      map.set(item.url, item)
    })
    return Array.from(map.values())
  })

  // 方法
  const addResult = (url: string, status: ParseStatus = 'idle', data: VideoData | null = null, error: string | null = null) => {
    const existingIndex = results.value.findIndex(r => r.url === url)

    if (existingIndex >= 0) {
      // 更新现有结果
      results.value[existingIndex] = {
        ...results.value[existingIndex],
        status,
        data,
        error,
        timestamp: Date.now()
      }
    } else {
      // 添加新结果
      results.value.push({
        id: `result-${Date.now()}-${Math.random()}`,
        url,
        status,
        data,
        error,
        timestamp: Date.now()
      })
    }
  }

  const updateResultStatus = (url: string, status: ParseStatus, data?: VideoData, error?: string) => {
    const result = results.value.find(r => r.url === url)

    if (result) {
      result.status = status
      if (data) result.data = data
      if (error) result.error = error
      result.timestamp = Date.now()
    }
  }

  const clearResults = () => {
    results.value = []
    isParsing.value = false
    currentUrlIndex.value = 0
  }

  const startParsing = (urls: string[]) => {
    clearResults()

    urls.forEach(url => {
      addResult(url, 'parsing')
    })

    isParsing.value = true
    currentUrlIndex.value = 0
  }

  const finishParsing = () => {
    isParsing.value = false
  }

  const removeResult = (url: string) => {
    const index = results.value.findIndex(r => r.url === url)

    if (index >= 0) {
      results.value.splice(index, 1)
    }
  }

  // Mock 方法（用于开发测试）
  const mockParseVideo = async (url: string): Promise<void> => {
    const platform = detectPlatform(url)

    await new Promise(resolve => setTimeout(resolve, 1000))

    let data: VideoData

    switch (platform) {
      case 'douyin':
        data = mockDouyinVideo
        break

      case 'tiktok':
        data = mockTikTokVideo
        break

      case 'bilibili':
        data = mockBilibiliVideo
        break

      default:
        // 对于无法识别的平台，使用抖音Mock数据进行演示
        data = mockDouyinVideo
    }

    updateResultStatus(url, 'success', data)
  }

  return {
    // 状态
    results,
    isParsing,
    currentUrlIndex,

    // 计算属性
    progress,
    uniqueResults,

    // 方法
    addResult,
    updateResultStatus,
    clearResults,
    startParsing,
    finishParsing,
    removeResult,
    mockParseVideo
  }
})

/**
 * 辅助函数：检测URL平台
 */
function detectPlatform(url: string): 'douyin' | 'tiktok' | 'bilibili' | 'unknown' {
  const lowerUrl = url.toLowerCase()

  if (lowerUrl.includes('douyin.com') || lowerUrl.includes('v.douyin.com')) {
    return 'douyin'
  }

  if (lowerUrl.includes('tiktok.com') || lowerUrl.includes('www.tiktok.com')) {
    return 'tiktok'
  }

  if (lowerUrl.includes('bilibili.com') || lowerUrl.includes('b23.tv')) {
    return 'bilibili'
  }

  return 'unknown'
}
