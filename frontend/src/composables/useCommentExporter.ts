import { ref } from 'vue'
import { ApiClient } from '@/api'

/**
 * 评论导出 Composable
 * @returns 评论导出相关方法和状态
 */
export function useCommentExporter() {
  const isExporting = ref(false)
  const isFetching = ref(false)
  const exportProgress = ref(0)
  const error = ref<string | null>(null)
  const downloadUrl = ref<string | null>(null)
  const comments = ref<any[]>([])
  const totalComments = ref(0)

  /**
   * 获取抖音评论
   * @param params 获取参数
   */
  const fetchDouyinComments = async (params: {
    aweme_id?: string
    url?: string
    max_comments: number
    cookie?: string
  }) => {
    try {
      error.value = null
      isFetching.value = true
      comments.value = []

      const data = await ApiClient.fetchDouyinComments(params)
      comments.value = data.comments
      const actualTotal = data.total || data.comments.length
      totalComments.value = Math.min(params.max_comments, actualTotal)

      return data
    } catch (err: any) {
      console.error('获取评论失败:', err)
      error.value = `获取失败: ${err.message || '未知错误'}`
      throw err
    } finally {
      isFetching.value = false
    }
  }

  /**
   * 获取TikTok评论
   * @param params 获取参数
   */
  const fetchTiktokComments = async (params: {
    aweme_id?: string
    url?: string
    max_comments: number
  }) => {
    try {
      error.value = null
      isFetching.value = true
      comments.value = []

      const data = await ApiClient.fetchTiktokComments(params)
      comments.value = data.comments
      const actualTotal = data.total || data.comments.length
      totalComments.value = Math.min(params.max_comments, actualTotal)

      return data
    } catch (err: any) {
      console.error('获取评论失败:', err)
      error.value = `获取失败: ${err.message || '未知错误'}`
      throw err
    } finally {
      isFetching.value = false
    }
  }

  /**
   * 导出抖音评论
   * @param params 导出参数
   */
  const exportDouyinComments = async (params: {
    aweme_id?: string
    url?: string
    max_comments: number
    cookie?: string
  }): Promise<Blob> => {
    try {
      error.value = null
      isExporting.value = true
      exportProgress.value = 0
      downloadUrl.value = null

      const blob = await ApiClient.exportDouyinComments(params)
      exportProgress.value = params.max_comments

      return blob
    } catch (err: any) {
      console.error('导出评论失败:', err)
      error.value = `导出失败: ${err.message || '未知错误'}`
      throw err
    } finally {
      isExporting.value = false
    }
  }

  /**
   * 导出TikTok评论
   * @param params 导出参数
   */
  const exportTiktokComments = async (params: {
    aweme_id?: string
    url?: string
    max_comments: number
  }): Promise<Blob> => {
    try {
      error.value = null
      isExporting.value = true
      exportProgress.value = 0
      downloadUrl.value = null

      const blob = await ApiClient.exportTiktokComments(params)
      exportProgress.value = params.max_comments

      return blob
    } catch (err: any) {
      console.error('导出评论失败:', err)
      error.value = `导出失败: ${err.message || '未知错误'}`
      throw err
    } finally {
      isExporting.value = false
    }
  }

  /**
   * 下载导出的CSV文件
   * @param blob Blob对象
   * @param filename 文件名
   */
  const downloadCSV = (blob: Blob, filename: string = 'comments.csv') => {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    downloadUrl.value = url
  }

  /**
   * 重置导出器
   */
  const resetExporter = () => {
    error.value = null
    isExporting.value = false
    exportProgress.value = 0
    downloadUrl.value = null
  }

  return {
    // 状态
    isExporting,
    isFetching,
    exportProgress,
    error,
    downloadUrl,
    comments,
    totalComments,

    // 方法
    fetchDouyinComments,
    fetchTiktokComments,
    exportDouyinComments,
    exportTiktokComments,
    downloadCSV,
    resetExporter
  }
}
