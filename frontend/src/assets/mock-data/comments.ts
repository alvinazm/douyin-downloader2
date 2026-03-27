import type { CommentExportParams } from '@/types/api'

export function createMockCSVFile(params: CommentExportParams): Blob {
  const csvContent = [
    '评论人,评论内容,点赞量,评论时间',
    `用户1,这是一条测试评论,123,${new Date().toISOString()}`,
    `用户2,这是第二条测试评论,456,${new Date().toISOString()}`,
    `用户3,这是第三条测试评论,789,${new Date().toISOString()}`
  ].join('\n')

  return new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
}
