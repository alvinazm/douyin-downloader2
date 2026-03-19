// 视频相关类型定义

/**
 * 解析状态枚举
 */
export enum ParseStatus {
  IDLE = 'idle',
  PARSING = 'parsing',
  SUCCESS = 'success',
  FAILED = 'failed'
}

/**
 * 视频结果项
 */
export interface VideoResultItem {
  id: string
  url: string
  status: ParseStatus
  data: VideoData | null
  error: string | null
  timestamp: number
}

/**
 * 视频解析进度
 */
export interface ParseProgress {
  total: number
  completed: number
  success: number
  failed: number
  currentUrl?: string
}

/**
 * 评论导出状态
 */
export enum ExportStatus {
  IDLE = 'idle',
  EXPORTING = 'exporting',
  SUCCESS = 'success',
  FAILED = 'failed'
}

/**
 * 评论导出结果
 */
export interface CommentExportResult {
  status: ExportStatus
  progress: number
  total: number
  downloaded: number
  error: string | null
  downloadUrl: string | null
}
