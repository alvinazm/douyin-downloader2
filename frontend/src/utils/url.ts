/**
 * URL 提取和验证工具函数
 */

const URL_REGEX = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/gi

/**
 * 从文本中提取所有URL
 * @param text 输入文本
 * @returns URL数组
 */
export function extractUrls(text: string): string[] {
  const matches = text.match(URL_REGEX)
  return matches ? matches : []
}

/**
 * 验证URL是否有效
 * @param url 待验证的URL
 * @returns 是否有效
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 识别URL所属平台
 * @param url URL字符串
 * @returns 平台类型
 */
export function detectPlatform(url: string): 'douyin' | 'tiktok' | 'bilibili' | 'unknown' {
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

/**
 * 格式化数字（如：10000 -> 1万）
 * @param number 数字
 * @returns 格式化后的字符串
 */
export function formatNumber(number: number): string {
  if (number >= 100000000) {
    return `${(number / 100000000).toFixed(1)}亿`
  }

  if (number >= 10000) {
    return `${(number / 10000).toFixed(1)}万`
  }

  return number.toString()
}

/**
 * 格式化时间戳
 * @param timestamp 时间戳（秒）
 * @returns 格式化后的日期字符串
 */
export function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const month = 30 * day
  const year = 365 * day

  if (diff < minute) {
    return '刚刚'
  }

  if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  }

  if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  }

  if (diff < month) {
    return `${Math.floor(diff / day)}天前`
  }

  if (diff < year) {
    return `${Math.floor(diff / month)}个月前`
  }

  return date.toLocaleDateString('zh-CN')
}

/**
 * 下载文件
 * @param url 文件URL
 * @param filename 文件名
 */
export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 复制文本到剪贴板
 * @param text 待复制的文本
 */
export async function copyToClipboard(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text)
  } catch (err) {
    console.error('复制失败:', err)
    throw new Error('复制失败')
  }
}

/**
 * 截断文本
 * @param text 待截断的文本
 * @param maxLength 最大长度
 * @returns 截断后的文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text
  }

  return text.substring(0, maxLength) + '...'
}
