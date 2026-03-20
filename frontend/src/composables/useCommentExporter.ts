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
  const currentTaskId = ref<string | null>(null)

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
   * 导出抖音评论（使用任务系统）
   * @param params 导出参数
   */
  const exportDouyinComments = async (params: {
    aweme_id?: string
    url?: string
    max_comments: number
    cookie?: string
  }) => {
    try {
      error.value = null
      isExporting.value = true
      exportProgress.value = 0
      downloadUrl.value = null
      currentTaskId.value = null

      let awemeId = params.aweme_id

      // 如果提供了URL但没有提供ID，则先提取ID
      if (!awemeId && params.url) {
        try {
          awemeId = await ApiClient.extractDouyinVideoId(params.url)
        } catch (err: any) {
          throw new Error('无法从URL获取视频ID，请检查链接是否正确')
        }
      }

      if (!awemeId) {
        throw new Error('无法获取视频ID')
      }

      // 创建任务
      const task = await ApiClient.createCommentExportTask({
        platform: 'douyin',
        aweme_id: awemeId,
        max_comments: params.max_comments,
        filename: `douyin_comments_${awemeId}`
      })

      currentTaskId.value = task.task_id

      return task
    } catch (err: any) {
      console.error('导出评论失败:', err)
      error.value = `导出失败: ${err.message || '未知错误'}`
      throw err
    } finally {
      isExporting.value = false
    }
  }

  /**
   * 导出TikTok评论（使用任务系统）
   * @param params 导出参数
   */
  const exportTiktokComments = async (params: {
    aweme_id?: string
    url?: string
    max_comments: number
  }) => {
    try {
      error.value = null
      isExporting.value = true
      exportProgress.value = 0
      downloadUrl.value = null
      currentTaskId.value = null

      let awemeId = params.aweme_id

      // 如果提供了URL但没有提供ID，则先提取ID
      if (!awemeId && params.url) {
        try {
          awemeId = await ApiClient.extractTiktokVideoId(params.url)
        } catch (err: any) {
          throw new Error('无法从URL获取视频ID，请检查链接是否正确')
        }
      }

      if (!awemeId) {
        throw new Error('无法获取视频ID')
      }

      // 创建任务
      const task = await ApiClient.createCommentExportTask({
        platform: 'tiktok',
        aweme_id: awemeId,
        max_comments: params.max_comments,
        filename: `tiktok_comments_${awemeId}`
      })

      currentTaskId.value = task.task_id

      return task
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
    currentTaskId.value = null
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
    currentTaskId,

    // 方法
    fetchDouyinComments,
    fetchTiktokComments,
    exportDouyinComments,
    exportTiktokComments,
    downloadCSV,
    resetExporter
  }
}
