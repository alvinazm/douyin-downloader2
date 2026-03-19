import { ref, toRef, computed } from 'vue'
import { useParserStore } from '@/stores/parser'
import type { VideoData } from '@/types/api'
import { ApiClient } from '@/api'

/**
 * 视频解析 Composable
 * @returns 解析相关方法和状态
 */
export function useVideoParser() {
  const parserStore = useParserStore()
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  /**
   * 解析单个URL
   * @param url 视频URL
   */
  const parseSingleUrl = async (url: string): Promise<VideoData | null> => {
    try {
      error.value = null

      // 调用API解析视频
      const data = await ApiClient.parseVideo({
        url,
        minimal: true
      })

      return data
    } catch (err: any) {
      console.error('解析失败:', url, err)
      error.value = `解析 ${url} 失败: ${err.message || '未知错误'}`
      return null
    }
  }

  /**
   * 批量解析URLs
   * @param urls URL数组
   */
  const parseMultipleUrls = async (urls: string[]): Promise<void> => {
    if (urls.length === 0) {
      error.value = '请输入至少一个有效的URL'
      return
    }

    isProcessing.value = true
    error.value = null

    parserStore.startParsing(urls)

    try {
      // 逐个解析（使用串行而非并发，防止触发风控）
      for (let i = 0; i < urls.length; i++) {
        const url = urls[i]

        try {
          // 使用真实API
          const data = await parseSingleUrl(url)

          if (data) {
            parserStore.updateResultStatus(url, 'success', data)
          } else {
            parserStore.updateResultStatus(url, 'failed', null, error.value || '解析失败')
          }
        } catch (err) {
          console.error(`解析 ${url} 时出错:`, err)
          parserStore.updateResultStatus(url, 'failed', null, err instanceof Error ? err.message : '未知错误')
        }

        // 更新当前解析的URL索引
        parserStore.currentUrlIndex = i + 1
      }
    } finally {
      isProcessing.value = false
      parserStore.finishParsing()
    }
  }

  /**
   * 重置解析器
   */
  const resetParser = () => {
    error.value = null
    isProcessing.value = false
    parserStore.clearResults()
  }

  return {
    // 状态
    isProcessing,
    error,

    // 计算属性（从store获取）
    progress: toRef(parserStore, 'progress'),
    results: toRef(parserStore, 'uniqueResults'),

    // 方法
    parseSingleUrl,
    parseMultipleUrls,
    resetParser
  }
}
