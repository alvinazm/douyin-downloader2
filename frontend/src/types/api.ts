// API 响应相关类型定义

/**
 * 通用响应模型
 */
export interface ResponseModel<T = any> {
  code: number
  router: string
  data: T
}

/**
 * 错误响应模型
 */
export interface ErrorResponseModel {
  code: number
  message: string
  support: string
  time: string
  router: string
  params: Record<string, any>
}

/**
 * 视频/图集标准数据模型
 */
export interface VideoData {
  type: 'video' | 'image'
  platform: 'douyin' | 'tiktok' | 'bilibili'
  video_id: string
  desc: string
  create_time: number
  author: AuthorInfo
  music: MusicInfo | null
  statistics: Statistics
  cover_data: CoverData
  hashtags: Hashtag[] | null
  video_data?: VideoUrls
  image_data?: ImageUrls
}

/**
 * 作者信息
 */
export interface AuthorInfo {
  nickname: string
  unique_id: string
  avatar_thumb?: string
  sec_uid?: string
  uid?: string  // Bilibili 使用
}

/**
 * 音乐信息
 */
export interface MusicInfo {
  id: string
  title: string
  author: string
  play_url: {
    url_list: string[]
  }
}

/**
 * 统计数据
 */
export interface Statistics {
  digg_count: number
  comment_count: number
  share_count: number
  play_count: number
  collect_count?: number
}

/**
 * 封面数据
 */
export interface CoverData {
  cover: string
  origin_cover: string
  dynamic_cover: string
}

/**
 * 话题标签
 */
export interface Hashtag {
  hashtag_name: string
  hashtag_id: string
}

/**
 * 视频URL集合
 */
export interface VideoUrls {
  wm_video_url: string
  wm_video_url_HQ: string
  nwm_video_url: string
  nwm_video_url_HQ: string
  audio_url?: string  // Bilibili 独有
}

/**
 * 图集URL集合
 */
export interface ImageUrls {
  no_watermark_image_list: string[]
  watermark_image_list: string[]
}

/**
 * 视频解析请求参数
 */
export interface VideoParseParams {
  url: string
  minimal: boolean
}

/**
 * 下载请求参数
 */
export interface DownloadParams {
  url: string
  prefix: boolean
  with_watermark: boolean
}

/**
 * 评论导出请求参数
 */
export interface CommentExportParams {
  aweme_id?: string
  url?: string
  max_comments: number
  cookie?: string
}

/**
 * 评论导出任务状态
 */
export interface CommentExportTask {
  task_id: string
  platform: 'douyin' | 'tiktok'
  aweme_id: string
  max_comments: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  total_fetched: number
  file_path: string
  error_message: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
  classification_status: 'none' | 'running' | 'completed' | 'failed'
  classification_progress: number
  classification_summary: Record<string, number> | null
  classified_file_path: string | null
}

/**
 * 创建任务响应
 */
export interface CreateTaskResponse {
  task_id: string
  platform: string
  aweme_id: string
  max_comments: number
  status: string
  file_path: string
  created_at: string
}

/**
 * iOS快捷指令信息
 */
export interface IOSShortcut {
  version: string
  update: string
  link: string
  link_en: string
  note: string
  note_en: string
}
