import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ResponseModel, ErrorResponseModel, VideoData, VideoParseParams, DownloadParams, CommentExportParams, IOSShortcut, CommentExportTask } from '@/types/api'
import { createMockCSVFile } from '@/assets/mock-data/comments'

/**
 * API 基础配置
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 是否使用Mock数据
 */
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true'

/**
 * 创建 Axios 实例
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 */
apiClient.interceptors.request.use(
  (config) => {
    // 添加 timestamp 防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse<ResponseModel>) => {
    return response
  },
  (error) => {
    const errorResponse: ErrorResponseModel = {
      code: error.response?.status || 500,
      message: error.message || '请求失败',
      support: 'Please contact us on Github',
      time: new Date().toISOString(),
      router: error.config?.url || '',
      params: error.config?.params || {}
    }

    return Promise.reject(errorResponse)
  }
)

/**
 * API 类 - 封装所有 API 调用
 */
export class ApiClient {
  /**
   * 解析视频/图集数据
   */
  static async parseVideo(params: VideoParseParams): Promise<VideoData> {
    const response: AxiosResponse<ResponseModel<VideoData>> = await apiClient.get('/hybrid/video_data', {
      params
    })

    return response.data.data
  }

  /**
   * 下载视频/图集
   */
  static async downloadFile(params: DownloadParams): Promise<Blob> {
    const response: AxiosResponse<Blob> = await apiClient.get('/download', {
      params,
      responseType: 'blob'
    })

    return response.data
  }

  /**
   * 提取抖音视频ID
   */
  static async extractDouyinVideoId(url: string): Promise<string> {
    const response: AxiosResponse<ResponseModel<string>> = await apiClient.get('/douyin/web/get_aweme_id', {
      params: { url }
    })

    return response.data.data as string
  }

  /**
   * 提取TikTok视频ID
   */
  static async extractTiktokVideoId(url: string): Promise<string> {
    const response: AxiosResponse<ResponseModel<string>> = await apiClient.get('/tiktok/web/get_aweme_id', {
      params: { url }
    })

    return response.data.data as string
  }

  /**
   * 获取抖音评论（预览）
   */
  static async fetchDouyinComments(params: CommentExportParams): Promise<any[]> {
    let awemeId = params.aweme_id

    // 如果提供了URL但没有提供ID，则先提取ID
    if (!awemeId && params.url) {
      try {
        const extractResponse: AxiosResponse<ResponseModel<string>> = await apiClient.get('/douyin/web/get_aweme_id', {
          params: {
            url: params.url
          }
        })
        awemeId = extractResponse.data.data as string
      } catch (err: any) {
        if (err.code === 400) {
          throw new Error('没有检测到有效的链接，请检查输入的内容是否正确。')
        }
        throw err
      }
    }

    if (!awemeId) {
      throw new Error('无法获取视频ID')
    }

    const response: AxiosResponse<ResponseModel<any>> = await apiClient.get('/douyin/web/fetch_video_comments', {
      params: {
        aweme_id: awemeId,
        cursor: 0,
        count: Math.min(params.max_comments || 100, 1000)
      }
    })

    const data = response.data.data as any
    const comments = data.comments || []

    return {
      comments: comments.map((comment: any) => ({
        comment_id: comment.cid,
        user_nickname: comment.user?.nickname || '未知用户',
        text: comment.text || '',
        digg_count: comment.digg_count || 0,
        create_time: comment.create_time ? new Date(comment.create_time * 1000).toISOString() : '',
        reply_count: comment.reply_to_reply_count || comment.reply_comment_total || 0,
        ip_label: comment.ip_label || ''
      })),
      total: data.total || comments.length
    }
  }

  /**
   * 获取TikTok评论（预览）
   */
  static async fetchTiktokComments(params: CommentExportParams): Promise<any> {
    let awemeId = params.aweme_id

    // 如果提供了URL但没有提供ID，则先提取ID
    if (!awemeId && params.url) {
      try {
        const extractResponse: AxiosResponse<ResponseModel<string>> = await apiClient.get('/tiktok/web/get_aweme_id', {
          params: {
            url: params.url
          }
        })
        awemeId = extractResponse.data.data as string
      } catch (err: any) {
        if (err.code === 400) {
          throw new Error('没有检测到有效的链接，请检查输入的内容是否正确。')
        }
        throw err
      }
    }

    if (!awemeId) {
      throw new Error('无法获取视频ID')
    }

    const response: AxiosResponse<ResponseModel<any>> = await apiClient.get('/tiktok/web/fetch_post_comment', {
      params: {
        aweme_id: awemeId,
        cursor: 0,
        count: Math.min(params.max_comments || 100, 1000),
        current_region: ''
      }
    })

    const data = response.data.data as any
    const comments = data.comments || []

    return {
      comments: comments.map((comment: any) => ({
        comment_id: comment.cid || comment.comment_id,
        user_nickname: comment.user?.nickname || comment.user?.unique_id || '未知用户',
        text: comment.text || comment.comment_text || '',
        digg_count: comment.digg_count || comment.like_count || 0,
        create_time: comment.create_time ? new Date(comment.create_time * 1000).toISOString() : '',
        reply_count: comment.reply_comment_total || 0,
        ip_label: comment.ip_label || ''
      })),
      total: data.total || comments.length
    }
  }

  /**
   * 导出抖音评论
   */
  static async exportDouyinComments(params: CommentExportParams): Promise<Blob> {
    if (USE_MOCK_DATA) {
      const mockBlob = createMockCSVFile(params)
      await new Promise(resolve => setTimeout(resolve, 1000))
      return mockBlob
    }

    let awemeId = params.aweme_id

    // 如果提供了URL但没有提供ID，则先提取ID
    if (!awemeId && params.url) {
      try {
        const extractResponse: AxiosResponse<ResponseModel<string>> = await apiClient.get('/douyin/web/get_aweme_id', {
          params: {
            url: params.url
          }
        })
        awemeId = extractResponse.data.data as string
      } catch (err: any) {
        if (err.code === 400) {
          throw new Error('没有检测到有效的链接，请检查输入的内容是否正确。')
        }
        throw err
      }
    }

    if (!awemeId) {
      throw new Error('无法获取视频ID')
    }

    const response: AxiosResponse<Blob> = await apiClient.get('/douyin/comments/export', {
      params: {
        aweme_id: awemeId,
        max_comments: params.max_comments
      },
      responseType: 'blob'
    })

    return response.data
  }

  /**
   * 导出TikTok评论
   */
  static async exportTiktokComments(params: CommentExportParams): Promise<Blob> {
    if (USE_MOCK_DATA) {
      const mockBlob = createMockCSVFile(params)
      await new Promise(resolve => setTimeout(resolve, 1000))
      return mockBlob
    }

    let awemeId = params.aweme_id

    // 如果提供了URL但没有提供ID，则先提取ID
    if (!awemeId && params.url) {
      try {
        const extractResponse: AxiosResponse<ResponseModel<string>> = await apiClient.get('/tiktok/web/get_aweme_id', {
          params: {
            url: params.url
          }
        })
        awemeId = extractResponse.data.data as string
      } catch (err: any) {
        if (err.code === 400) {
          throw new Error('没有检测到有效的链接，请检查输入的内容是否正确。')
        }
        throw err
      }
    }

    if (!awemeId) {
      throw new Error('无法获取视频ID')
    }

    const response: AxiosResponse<Blob> = await apiClient.get('/tiktok/comments/export', {
      params: {
        aweme_id: awemeId,
        max_comments: params.max_comments
      },
      responseType: 'blob'
    })

    return response.data
  }

  /**
   * 获取iOS快捷指令信息
   */
  static async getIOSShortcut(): Promise<IOSShortcut> {
    const response: AxiosResponse<ResponseModel<IOSShortcut>> = await apiClient.get('/ios/shortcut')

    return response.data.data
  }

  /**
   * 更新Cookie
   */
  static async updateCookie(service: string, cookie: string): Promise<{ message: string }> {
    const response: AxiosResponse<ResponseModel<{ message: string }>> = await apiClient.post('/hybrid/update_cookie', {
      service,
      cookie
    })

    return response.data.data
  }

  /**
   * 创建评论导出任务
   */
  static async createCommentExportTask(params: {
    platform: 'douyin' | 'tiktok'
    aweme_id: string
    max_comments: number
    filename?: string
  }) {
    const response: AxiosResponse<ResponseModel<any>> = await apiClient.post('/tasks/comments/create_task', null, {
      params
    })

    return response.data.data
  }

  /**
   * 获取任务状态
   */
  static async getTaskStatus(task_id: string): Promise<CommentExportTask> {
    const response: AxiosResponse<ResponseModel<CommentExportTask>> = await apiClient.get(`/tasks/comments/tasks/${task_id}`)

    return response.data.data
  }

  /**
   * 获取所有任务
   */
  static async getAllTasks(): Promise<{ total: number; tasks: CommentExportTask[] }> {
    const response: AxiosResponse<ResponseModel<{ total: number; tasks: CommentExportTask[] }>> = await apiClient.get('/tasks/comments/tasks')

    console.log('getAllTasks - response:', response)
    console.log('getAllTasks - response.data:', response.data)
    console.log('getAllTasks - response.data.data:', response.data.data)

    return response.data.data
  }

  /**
   * 下载任务文件
   */
  static async downloadTaskFile(task_id: string): Promise<Blob> {
    const response: AxiosResponse<Blob> = await apiClient.get(`/tasks/comments/download/${task_id}`, {
      responseType: 'blob'
    })

    return response.data
  }

  /**
   * 删除任务
   */
  static async deleteTask(task_id: string, delete_file: boolean = false): Promise<{ task_id: string; delete_file: boolean }> {
    const response: AxiosResponse<ResponseModel<{ task_id: string; delete_file: boolean }>> = await apiClient.delete(`/tasks/comments/tasks/${task_id}`, {
      params: { delete_file }
    })

    return response.data.data
  }
}

export default apiClient
