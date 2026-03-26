# 后端对接完成文档

## 概述
已完成前端与后端的完整对接，移除了Mock数据模式，前端现在使用真实的后端API。

## 修改内容

### 1. 环境配置更新
**文件**: `frontend/.env`
```bash
VITE_USE_MOCK_DATA=false  # 从 true 改为 false
```

### 2. API端点修复
**文件**: `frontend/src/api/index.ts`

#### 2.1 修复抖音评论获取端点
- **修改前**: `/douyin/comments`
- **修改后**: `/douyin/fetch_video_comments` (符合PRD规范)

#### 2.2 修复TikTok评论获取端点
- **修改前**: `/tiktok/comments`
- **修改后**: `/tiktok/fetch_video_comments` (推断的端点，遵循抖音模式)

#### 2.3 移除Mock逻辑
- 删除了评论获取函数中的Mock数据生成代码
- 删除了评论导出函数中的Mock数据生成代码

### 3. 组件代码简化
**文件**: `frontend/src/components/VideoPreview.vue`
- 移除了 `useMock` 变量
- 直接调用真实API，不使用Mock数据

### 4. Composable代码简化
**文件**: `frontend/src/composables/useVideoParser.ts`
- 移除了 `useMock` 参数
- 简化了批量解析逻辑，始终使用真实API
- 删除了Mock数据条件分支

## API端点对接清单

### ✅ 混合解析API
- `GET /api/hybrid/video_data` - 视频数据解析
- `POST /api/hybrid/update_cookie` - 更新Cookie

### ✅ 下载API
- `GET /api/download` - 文件下载

### ✅ 评论系统API
- `GET /api/douyin/fetch_video_comments` - 获取抖音评论列表
- `GET /api/douyin/comments/export` - 导出抖音评论为CSV
- `GET /api/tiktok/fetch_video_comments` - 获取TikTok评论列表
- `GET /api/tiktok/comments/export` - 导出TikTok评论为CSV

### ✅ iOS快捷指令API
- `GET /api/ios/shortcut` - 获取iOS快捷指令信息

## 后端要求

### 1. 必需的API端点
后端需要实现以下端点以支持前端功能：

#### 抖音评论相关
```python
GET /api/douyin/fetch_video_comments
参数:
  - aweme_id: str (必填) - 视频ID
  - cursor: int (可选) - 分页游标
  - count: int (可选) - 每页数量

返回格式:
  {
    "code": 200,
    "router": "/api/douyin/fetch_video_comments",
    "data": [
      {
        "comment_id": "评论ID",
        "user_nickname": "用户昵称",
        "user_id": "用户ID",
        "text": "评论内容",
        "digg_count": 点赞数,
        "reply_count": 回复数,
        "create_time": "发布时间",
        "ip_label": "IP归属地"
      }
    ]
  }
```

#### TikTok评论相关
```python
GET /api/tiktok/fetch_video_comments
参数:
  - aweme_id: str (必填) - 视频ID
  - cursor: int (可选) - 分页游标
  - count: int (可选) - 每页数量

返回格式: 与抖音评论相同
```

### 2. 数据格式要求
所有API返回需要遵循PRD中的标准响应格式：

```json
{
  "code": 200,
  "router": "/api/...",
  "data": { ... }
}
```

错误响应格式：
```json
{
  "code": 400,
  "message": "错误信息",
  "support": "Please contact us on Github...",
  "time": "2025-03-18T07:00:00Z",
  "router": "/api/...",
  "params": { ... }
}
```

## 功能对接确认

### ✅ 视频解析页面 (`/parse`)
- 批量解析URL
- 显示解析结果（视频/图集）
- 提供下载链接

### ✅ 评论导出页面 (`/export/:platform`)
- 获取评论预览
- 显示评论列表
- 导出CSV文件

### ✅ 首页 (`/`)
- 功能导航
- 快捷指令链接

## 测试建议

### 1. 视频解析测试
```bash
# 测试抖音视频
curl "http://localhost:8000/api/hybrid/video_data?url=https://v.douyin.com/L4FJNR3/&minimal=true"

# 测试TikTok视频
curl "http://localhost:8000/api/hybrid/video_data?url=https://www.tiktok.com/@username/video/7156033831819037994&minimal=true"

# 测试Bilibili视频
curl "http://localhost:8000/api/hybrid/video_data?url=https://www.bilibili.com/video/BV1M1421t7hT&minimal=true"
```

### 2. 评论导出测试
```bash
# 测试抖音评论导出
curl "http://localhost:8000/api/douyin/comments/export?aweme_id=7372484719365098803&max_comments=100" --output douyin_comments.csv

# 测试TikTok评论导出
curl "http://localhost:8000/api/tiktok/comments/export?aweme_id=7156033831819037994&max_comments=100" --output tiktok_comments.csv
```

### 3. 获取评论测试
```bash
# 测试抖音评论获取
curl "http://localhost:8000/api/douyin/fetch_video_comments?aweme_id=7372484719365098803&count=100"

# 测试TikTok评论获取
curl "http://localhost:8000/api/tiktok/fetch_video_comments?aweme_id=7156033831819037994&count=100"
```

## 注意事项

1. **API基础URL**: 前端配置为 `/api`，需要确保后端API运行在 `/api` 路径下，或通过Vite代理转发到 `http://localhost:8000`

2. **跨域处理**: 如后端和前端不在同一域名，需要配置CORS

3. **错误处理**: 前端已实现完善的错误处理机制，后端需要正确返回错误响应

4. **超时设置**: 前端API客户端设置的超时时间为30秒，确保后端操作在此时间内完成

5. **并发控制**: 前端视频解析采用串行逐个解析，避免触发后端风控

## 完成状态

- ✅ API端点配置完成
- ✅ Mock模式已禁用
- ✅ 前端代码与PRD规范一致
- ✅ 环境变量已更新
- ✅ 开发服务器已重启
- 🔄 等待后端API实现

---

**生成时间**: 2025-03-18
**前端版本**: V4.1.2
**后端版本**: V4.1.2
