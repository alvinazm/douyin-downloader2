import { ref } from 'vue'
import { ApiClient } from '@/api'
import { downloadFile } from '@/utils/url'

/**
 * 文件下载 Composable
 * @returns 下载相关方法和状态
 */
export function useDownloader() {
  const isDownloading = ref(false)
  const downloadProgress = ref(0)
  const error = ref<string | null>(null)

  /**
   * 下载视频/图集
   * @param url 源URL
   * @param withWatermark 是否下载带水印版本
   * @param prefix 是否添加文件前缀
   */
  const downloadMedia = async (
    url: string,
    withWatermark: boolean = false,
    prefix: boolean = true
  ): Promise<void> => {
    try {
      error.value = null
      isDownloading.value = true
      downloadProgress.value = 0

      // 调用API下载
      const blob = await ApiClient.downloadFile({
        url,
        with_watermark: withWatermark,
        prefix
      })

      // 从Content-Disposition头获取文件名，如果没有则使用默认文件名
      let filename = `download_${withWatermark ? 'with_watermark' : 'no_watermark'}`
      const contentDisposition = blob.type

      // 根据内容类型确定扩展名
      if (contentDisposition.startsWith('video/')) {
        filename += '.mp4'
      } else if (contentDisposition.startsWith('application/zip')) {
        filename += '.zip'
      }

      // 创建下载链接
      const downloadUrl = URL.createObjectURL(blob)
      downloadFile(downloadUrl, filename)

      downloadProgress.value = 100
    } catch (err: any) {
      console.error('下载失败:', err)
      error.value = `下载失败: ${err.message || '未知错误'}`
      throw err
    } finally {
      isDownloading.value = false
    }
  }

  /**
   * 重置下载器
   */
  const resetDownloader = () => {
    error.value = null
    isDownloading.value = false
    downloadProgress.value = 0
  }

  return {
    // 状态
    isDownloading,
    downloadProgress,
    error,

    // 方法
    downloadMedia,
    resetDownloader
  }
}
