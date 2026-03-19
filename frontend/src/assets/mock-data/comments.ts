import type { CommentExportParams } from '@/types/api'

export const generateMockCommentsCSV = (params: CommentExportParams): string => {
  const count = params.max_comments || 100
  const awemeId = params.aweme_id || 'unknown'
  const timestamp = Date.now()
  
  const headers = ['编号', '评论ID', '用户昵称', '用户ID', '评论内容', '点赞数', '回复数', '发布时间', 'IP归属地']
  const rows: string[] = [headers.join(',')]
  
  for (let i = 1; i <= count; i++) {
    const row = [
      i,
      `comment_${awemeId}_${i}`,
      `用户${i}`,
      `user_${i}`,
      `这是第${i}条评论内容，来自视频 ${awemeId} 的模拟数据`,
      Math.floor(Math.random() * 1000),
      Math.floor(Math.random() * 100),
      new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      ['北京', '上海', '广州', '深圳', '杭州', '成都'][Math.floor(Math.random() * 6)]
    ]
    rows.push(row.join(','))
  }
  
  return rows.join('\n')
}

export const createMockCSVFile = (params: CommentExportParams): Blob => {
  const csvContent = generateMockCommentsCSV(params)
  return new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
}
