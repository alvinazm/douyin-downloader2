#  技术方案：前端 + 后端

## 1. 技术架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (Vue.js SPA)                       │
│  Vue 3 + Vite 5 + TypeScript + Tailwind CSS + Pinia + Axios     │
└─────────────────────────────────────────────────────────────────┘
                                │ HTTP/REST
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端 (Python FastAPI)                    │
│        FastAPI + Uvicorn + httpx + Pydantic + Crawlers          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 前端架构

### 2.1 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue.js | 3.x (Composition API) |
| 构建工具 | Vite | 5.x |
| 语言 | TypeScript | 5.x |
| 路由 | Vue Router | 4.x |
| 状态管理 | Pinia | 2.x |
| HTTP客户端 | Axios | 1.x |
| CSS框架 | Tailwind CSS | 3.x |

### 2.2 项目结构

```
frontend/src/
├── api/
│   └── index.ts              # API客户端类 (ApiClient)
├── components/
│   ├── MainView.vue          # 首页 /
│   ├── ParsePage.vue         # 批量解析页 /parse
│   ├── VideoPreview.vue      # 解析核心组件
│   ├── ExportPage.vue        # 评论导出页 /export/:platform
│   ├── CommentExport.vue     # 导出核心组件
│   └── DownloadHistory.vue   # 导出记录页 /download-history
├── composables/
│   ├── useVideoParser.ts     # 视频解析逻辑
│   ├── useCommentExporter.ts # 评论导出逻辑
│   ├── useTaskManager.ts     # 任务管理逻辑
│   ├── useDownloader.ts      # 文件下载逻辑
│   └── useToast.ts           # Toast通知
├── router/
│   └── index.ts              # Vue Router配置
├── stores/
│   ├── config.ts             # 配置状态管理
│   └── parser.ts             # 解析器状态管理
├── types/
│   ├── api.ts                # API相关类型定义
│   └── video.ts              # 视频相关类型定义
├── utils/
│   └── url.ts                # URL工具函数
└── App.vue                   # 根组件
```

### 2.3 路由配置

| 路径 | 组件 | 描述 |
|------|------|------|
| `/` | `MainView.vue` | 首页 |
| `/parse` | `ParsePage.vue` (懒加载) | 批量解析 |
| `/export/:platform` | `ExportPage.vue` (懒加载) | 评论导出 (platform: douyin/tiktok) |
| `/download-history` | `DownloadHistory.vue` (懒加载) | 导出记录 |

---

## 3. 前端类型定义

### 3.1 核心类型 (`types/api.ts`)

```typescript
// 通用响应模型
interface ResponseModel<T = any> {
  code: number
  router: string
  data: T
}

// 视频数据模型
interface VideoData {
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

interface AuthorInfo {
  nickname: string
  unique_id: string
  avatar_thumb?: string
  sec_uid?: string
  uid?: string
}

interface VideoUrls {
  wm_video_url: string
  wm_video_url_HQ: string
  nwm_video_url: string
  nwm_video_url_HQ: string
  audio_url?: string
}

interface ImageUrls {
  no_watermark_image_list: string[]
  watermark_image_list: string[]
}

// 评论导出任务
interface CommentExportTask {
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
```

### 3.2 解析状态 (`types/video.ts`)

```typescript
enum ParseStatus {
  IDLE = 'idle',
  PARSING = 'parsing',
  SUCCESS = 'success',
  FAILED = 'failed'
}

interface VideoResultItem {
  id: string
  url: string
  status: ParseStatus
  data: VideoData | null
  error: string | null
  timestamp: number
}

interface ParseProgress {
  total: number
  completed: number
  success: number
  failed: number
  currentUrl?: string
}
```

---

## 4. API客户端 (`api/index.ts`)

### 4.1 核心方法

| 方法 | HTTP | 路径 | 描述 |
|------|------|------|------|
| `parseVideo(params)` | GET | `/hybrid/video_data` | 解析视频 |
| `downloadFile(params)` | GET | `/download` | 下载视频 |
| `extractDouyinVideoId(url)` | GET | `/douyin/web/get_aweme_id` | 提取抖音视频ID |
| `extractTiktokVideoId(url)` | GET | `/tiktok/web/get_aweme_id` | 提取TikTok视频ID |
| `fetchDouyinComments(params)` | GET | `/douyin/web/fetch_video_comments` | 获取抖音评论预览 |
| `fetchTiktokComments(params)` | GET | `/tiktok/web/fetch_post_comment` | 获取TikTok评论预览 |
| `exportDouyinComments(params)` | GET | `/douyin/comments/export` | 导出抖音评论 |
| `exportTiktokComments(params)` | GET | `/tiktok/comments/export` | 导出TikTok评论 |
| `createCommentExportTask(params)` | POST | `/tasks/comments/create_task` | 创建导出任务 |
| `getAllTasks()` | GET | `/tasks/comments/tasks` | 获取所有任务 |
| `getTaskStatus(taskId)` | GET | `/tasks/comments/tasks/{task_id}` | 获取任务状态 |
| `downloadTaskFile(taskId)` | GET | `/tasks/comments/download/{task_id}` | 下载任务文件 |
| `deleteTask(taskId, deleteFile)` | DELETE | `/tasks/comments/tasks/{task_id}` | 删除任务 |
| `startClassify(taskId, batchSize, workers)` | POST | `/tasks/comments/classify/{task_id}` | 启动AI分类 |
| `getClassifyStatus(taskId)` | GET | `/tasks/comments/classification_status/{task_id}` | 获取分类状态 |
| `downloadClassifiedFile(taskId)` | GET | `/tasks/comments/download_classified/{task_id}` | 下载已分类文件 |
| `getConfig()` | GET | `/config/config` | 获取配置 |
| `getIOSShortcut()` | GET | `/ios/shortcut` | 获取iOS快捷指令信息 |

---

## 5. 状态管理

### 5.1 ConfigStore (`stores/config.ts`)

```typescript
interface ConfigState {
  apiVersion: string
  updateTime: string
  environment: string       // 'Production' | 'Demo'
  maxTakeUrls: number       // 一次最多解析URL数 (默认30)
  maxComments: number        // 最大评论导出数 (默认50000)
  downloadSwitch: boolean
  downloadFilePrefix: string
  easterEgg: boolean
  live2DEnable: boolean
  isLoading: boolean
  error: string | null
}
```

### 5.2 ParserStore (`stores/parser.ts`)

```typescript
interface ParserState {
  results: VideoResultItem[]
  isParsing: boolean
  currentUrlIndex: number
}

interface ParserGetters {
  progress: ParseProgress       // { total, completed, success, failed, currentUrl }
  uniqueResults: VideoResultItem[]
}
```

---

## 6. Composables

### 6.1 useVideoParser

```typescript
function useVideoParser() {
  // State
  isProcessing: Ref<boolean>
  error: Ref<string | null>
  
  // From store
  progress: ToRef<ParseProgress>
  results: ToRef<VideoResultItem[]>
  
  // Methods
  parseSingleUrl(url: string): Promise<VideoData | null>
  parseMultipleUrls(urls: string[]): Promise<void>
  resetParser(): void
}
```

### 6.2 useCommentExporter

```typescript
function useCommentExporter() {
  // State
  isFetching: Ref<boolean>
  isExporting: Ref<boolean>
  exportProgress: Ref<number>
  error: Ref<string | null>
  comments: Ref<any[]>
  totalComments: Ref<number>
  currentTaskId: Ref<string | null>
  
  // Methods
  fetchDouyinComments(params): Promise<{ comments, total }>
  fetchTiktokComments(params): Promise<{ comments, total }>
  exportDouyinComments(params): Promise<any>
  exportTiktokComments(params): Promise<any>
  downloadCSV(blob: Blob, filename: string): void
  resetExporter(): void
}
```

### 6.3 useTaskManager

```typescript
function useTaskManager() {
  // State (模块级单例)
  tasks: Ref<CommentExportTask[]>
  isPolling: Ref<boolean>
  
  // Getters
  sortedTasks: ComputedRef<CommentExportTask[]>  // 按created_at降序
  
  // Methods
  loadAllTasks(): Promise<{ total, tasks }>
  getTaskStatus(taskId: string): Promise<CommentExportTask | null>
  startPolling(interval?: number): void   // 默认5000ms
  stopPolling(): void
  downloadTaskFile(taskId: string, filename: string): Promise<void>
  deleteTask(taskId: string, deleteFile?: boolean): Promise<void>
  clearAllTasks(): void
}
```

---

## 7. 页面详细设计

### 7.1 首页 `/` (MainView.vue)

**功能：** 功能导航入口

**组件结构：**
- Logo + 标题区
- 4个功能卡片网格
- Footer
- Modal (iOS Shortcuts / API Docs / About / Easter Egg)

**功能卡片：**

| ID | 路由 | 图标 | 标题 |
|----|------|------|------|
| parse | `/parse` | 🔍 | 批量解析视频 |
| export-douyin-id | `/export/douyin` | 💬 | 导出抖音评论 |
| export-tiktok-id | `/export/tiktok` | 🎬 | 导出TikTok评论 |
| download-history | `/download-history` | 📥 | 导出记录 |

### 7.2 批量解析页 `/parse` (ParsePage.vue + VideoPreview.vue)

**功能：** 批量解析并下载无水印视频/图集

**VideoPreview.vue 核心逻辑：**

```
用户输入URLs
    │
    ▼
validateInput() ──检查URL数量──▶ 超过maxTakeUrls ──▶ 显示错误Modal
    │
    │ 通过
    ▼
parseMultipleUrls(urls)
    │
    ├── 逐个调用 ApiClient.parseVideo({ url, minimal: true })
    │
    ├── 实时更新 parserStore.results (状态: parsing → success/failed)
    │
    └── 完成后 isParsing = false
```

**状态展示：**

| 状态 | 样式 | 内容 |
|------|------|------|
| parsing | 黄色旋转 | 平台、URL |
| success-video | 绿色勾 | 平台、类型、描述、作者、下载按钮 |
| success-image | 绿色勾 | 平台、类型、描述、作者、图片网格 |
| failed | 红色叉 | 错误信息 |

### 7.3 评论导出页 `/export/:platform` (ExportPage.vue + CommentExport.vue)

**功能：** 评论预览和导出任务创建

**CommentExport.vue 核心逻辑：**

```
用户输入 (URL 或 ID)
    │
    ▼
handleFetch()
    │
    ├── exportType === 'url' → extractVideoId(url)
    ├── exportType === 'id' → 直接使用 aweme_id
    ▼
fetchDouyinComments / fetchTiktokComments
    │
    ├── 获取前5条预览
    └── hasFetched = true
    │
    ▼
handleExport()
    │
    ├── createCommentExportTask()
    └── currentTaskId = task.task_id
    │
    ▼
显示「查看导出进度」按钮 → 跳转 /download-history
```

**输入模式切换：**
- `exportType = 'url'` → 显示 textarea（输入分享链接）
- `exportType = 'id'` → 显示 input（输入视频ID）

### 7.4 导出记录页 `/download-history` (DownloadHistory.vue)

**功能：** 任务列表管理、进度监控、AI分类

**生命周期：**
```typescript
onMounted(async () => {
  await loadAllTasks()
  
  // 对每个 running 的分类任务恢复轮询
  tasks.value.forEach(task => {
    if (task.classification_status === 'running') {
      pollClassificationStatus(task.task_id)
    }
  })
  
  startPolling()  // 对 running 状态任务全局轮询
})

onUnmounted(() => {
  stopPolling()
  Object.values(classificationPollIntervals).forEach(clearInterval)
})
```

**任务状态流转：**
```
pending → running → completed
                 └→ failed
```

**AI分类流程：**
```
handleClassify(task)
    │
    ├── ApiClient.startClassify(taskId, 20, 5)
    │
    └── pollClassificationStatus(taskId)
            │
            ├── 每5秒轮询 getClassifyStatus
            ├── 更新 classifyProgress[taskId]
            ├── completed → alert显示统计 + loadAllTasks()
            └── failed → alert显示错误
```

---

## 8. 后端架构

### 8.1 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | FastAPI |
| ASGI服务器 | Uvicorn |
| HTTP客户端 | httpx (异步) |
| 数据验证 | Pydantic |
| 爬虫框架 | 自研 `BaseCrawler` |

### 8.2 项目结构

```
app/
├── api/
│   ├── router.py              # 路由聚合
│   ├── models/
│   │   └── APIResponseModel.py  # 响应模型
│   └── endpoints/
│       ├── tiktok_web.py      # TikTok Web API
│       ├── tiktok_app.py       # TikTok App API
│       ├── douyin_web.py       # 抖音 Web API
│       ├── bilibili_web.py     # Bilibili Web API
│       ├── hybrid_parsing.py   # 混合解析
│       ├── download.py         # 下载服务
│       ├── comment_export.py   # 抖音评论导出
│       ├── tiktok_comment_export.py  # TikTok评论导出
│       ├── comment_export_task_api.py  # 任务管理API
│       ├── config_api.py       # 配置API
│       └── ios_shortcut.py     # iOS快捷指令
├── web/
│   └── app.py                 # PyWebIO旧版界面
├── main.py                    # PyWebIO入口
├── vue_main.py                # Vue SPA入口
└── config.py                  # 配置加载

crawlers/
├── base_crawler.py            # 基础爬虫类
├── douyin/
│   └── web/
│       ├── web_crawler.py     # 抖音爬虫
│       ├── models.py          # 请求模型
│       └── endpoints.py       # API端点
├── tiktok/
│   └── web/
│       ├── web_crawler.py     # TikTok爬虫
│       ├── models.py
│       └── endpoints.py
└── bilibili/
    └── web/
        ├── web_crawler.py
        ├── models.py
        └── endpoints.py
```

---

## 9. 后端API端点

### 9.1 混合解析 API

| 方法 | 路径 | 参数 | 返回 |
|------|------|------|------|
| GET | `/hybrid/video_data` | `url`, `minimal` | `VideoData` |

### 9.2 抖音 Web API

| 方法 | 路径 | 参数 | 返回 |
|------|------|------|------|
| GET | `/douyin/web/get_aweme_id` | `url` | `string` |
| GET | `/douyin/web/fetch_video_comments` | `aweme_id`, `cursor`, `count` | `{ comments, total }` |
| GET | `/douyin/web/fetch_video_comment_replies` | `item_id`, `comment_id`, `cursor`, `count` | 评论回复 |

### 9.3 TikTok Web API

| 方法 | 路径 | 参数 | 返回 |
|------|------|------|------|
| GET | `/tiktok/web/get_aweme_id` | `url` | `string` |
| GET | `/tiktok/web/fetch_post_comment` | `aweme_id`, `cursor`, `count`, `current_region` | `{ comments, total }` |

### 9.4 下载 API

| 方法 | 路径 | 参数 | 返回 |
|------|------|------|------|
| GET | `/download` | `url`, `prefix`, `with_watermark` | `Blob` (文件流) |

### 9.5 任务管理 API

| 方法 | 路径 | 参数 | 返回 |
|------|------|------|------|
| POST | `/tasks/comments/create_task` | `platform`, `aweme_id`, `max_comments`, `filename` | `CommentExportTask` |
| GET | `/tasks/comments/tasks` | - | `{ total, tasks: CommentExportTask[] }` |
| GET | `/tasks/comments/tasks/{task_id}` | - | `CommentExportTask` |
| DELETE | `/tasks/comments/tasks/{task_id}` | `delete_file` | `{ task_id, delete_file }` |
| POST | `/tasks/comments/classify/{task_id}` | `batch_size`, `workers` | `{ task_id, status, message }` |
| GET | `/tasks/comments/classification_status/{task_id}` | - | 分类状态对象 |
| GET | `/tasks/comments/download/{task_id}` | - | `Blob` |
| GET | `/tasks/comments/download_classified/{task_id}` | - | `Blob` |

### 9.6 配置 API

| 方法 | 路径 | 返回 |
|------|------|------|
| GET | `/config/config` | `{ maxComments, maxTakeUrls, apiVersion, environment }` |

---

## 10. 数据模型

### 10.1 Pydantic响应模型

```python
class ResponseModel(BaseModel):
    code: int = 200
    router: str
    data: Optional[Any] = {}

class ErrorResponseModel(BaseModel):
    code: int = 400
    message: str
    support: str
    time: str
    router: str
    params: dict = {}
```

### 10.2 评论导出任务模型

```python
class CommentExportTask:
    task_id: str
    platform: str               # 'douyin' | 'tiktok'
    aweme_id: str
    max_comments: int
    file_path: str
    status: str                 # 'pending' | 'running' | 'completed' | 'failed'
    progress: int               # 0-100
    total_fetched: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    classification_status: Optional[str]  # 'none' | 'running' | 'completed' | 'failed'
    classification_progress: int
    classification_summary: Optional[Dict[str, int]]
    classified_file_path: Optional[str]
```

---

## 11. 任务管理系统

### 11.1 架构

- **无Redis/Celery** - 使用内存字典 `Dict[str, CommentExportTask]` 管理任务
- **异步执行** - 使用 `asyncio` + FastAPI `BackgroundTasks`
- **客户端轮询** - 前端每5秒轮询 `/tasks/comments/tasks/{task_id}` 获取状态

### 11.2 执行流程

```
1. POST /tasks/comments/create_task
      │
      ▼
   创建 Task → status='pending'
      │
      ▼
   返回 task_id 给前端
      │
      ▼
2. 后台 BackgroundTasks 执行 execute_task()
      │
      ├── status = 'running'
      │
      ├── 循环获取评论 (cursor分页)
      │
      ├── 实时写入CSV文件
      │
      ├── 更新 progress
      │
      └── status = 'completed' 或 'failed'
```

### 11.3 CSV字段

| 字段 | 说明 |
|------|------|
| 评论人 | 用户昵称 |
| 评论内容 | 评论文本 |
| 点赞量 | digg_count |
| 评论时间 | ISO格式时间戳 |

---

## 12. AI评论分类

### 12.1 流程

```
POST /tasks/comments/classify/{task_id}
    │
    ├── 启动异步分类任务 (ThreadPoolExecutor)
    │
    ├── 读取原CSV文件
    │
    ├── 分批调用 MiniMax API (OpenAI兼容接口)
    │
    │   每批: batch_size=20, workers=5
    │
    ├── 写入分类结果到新CSV
    │
    └── 更新 classification_status
```

### 12.2 分类统计

```python
classification_summary: {
    'positive': 120,
    'negative': 45,
    'neutral': 200
}
```

---

## 13. 爬虫模块架构

### 13.1 BaseCrawler

```python
class BaseCrawler:
    def __init__(
        self,
        proxies: dict = None,
        max_retries: int = 3,
        timeout: int = 10,
        max_tasks: int = 50
    )
    
    async def fetch_get_json(endpoint: str) -> dict
    async def fetch_post_json(endpoint: str, params: dict, data: any) -> dict
    async def get_fetch_data(url: str) -> response
```

### 13.2 错误处理

```
APIError
├── APIConnectionError
├── APIUnavailableError
├── APINotFoundError
├── APIResponseError
├── APIRateLimitError (429)
├── APITimeoutError
├── APIUnauthorizedError
└── APIRetryExhaustedError
```

### 13.3 签名生成

| 平台 | 签名 |
|------|------|
| 抖音 | X-Bogus, A-Bogus, msToken, ttwid |
| TikTok | X-Bogus, msToken, ttwid, odin_tt |
| Bilibili | w_rid, wbi签名 |

---

## 14. 配置管理

### 14.1 config.yaml

```yaml
API:
  Version: "V4.1.2"
  Environment: "Demo"        # Demo | Production
  Max_Comments: 50000        # 最大评论导出数
  Max_Take_URLs: 30          # 一次最多解析URL数
  Download_Switch: true
  Download_Path: "./download"
  Download_File_Prefix: "douyin.wtf_"

Web:
  PyWebIO_Enable: true
  Max_Take_URLs: 30
  Easter_Egg: true
  Live2D_Enable: true
```

### 14.2 前端环境变量

```bash
VITE_API_BASE_URL=/api      # API基础路径
VITE_USE_MOCK_DATA=false    # 是否使用Mock数据
```

---

## 15. 页面数据流图

### 15.1 批量解析数据流

```
┌──────────────────────────────────────────────────────────────────┐
│                        VideoPreview.vue                          │
├──────────────────────────────────────────────────────────────────┤
│  inputText (用户输入URLs)                                        │
│       │                                                          │
│       ▼                                                          │
│  validateInput()                                                  │
│       │                                                          │
│       ▼                                                          │
│  parseMultipleUrls(urls) ──────────────┐                         │
│       │                               │                          │
│       ▼                               │                          │
│  parserStore.startParsing(urls)        │                          │
│       │                               │                          │
│       ▼                               │                          │
│  循环: parseSingleUrl(url)             │                          │
│       │                               │                          │
│       ├── 成功 → store.updateResult   │                          │
│       │           (status='success')  │                          │
│       │                               │                          │
│       └── 失败 → store.updateResult   │                          │
│                   (status='failed')   │                          │
│                                          │                       │
│       ◀─────────────────────────────────┘                       │
│       │                                                          │
│       ▼                                                          │
│  results (展示解析结果)                                           │
│       │                                                          │
│       ▼                                                          │
│  downloadVideo() → GET /api/download?url=... → Blob → 下载      │
└──────────────────────────────────────────────────────────────────┘
```

### 15.2 评论导出数据流

```
┌──────────────────────────────────────────────────────────────────┐
│                      CommentExport.vue                           │
├──────────────────────────────────────────────────────────────────┤
│  用户输入 (URL/ID + maxComments)                                 │
│       │                                                          │
│       ▼                                                          │
│  handleFetch()                                                    │
│       │                                                          │
│       ├── URL模式 → extractVideoId(url) → aweme_id               │
│       │                                                          │
│       └── fetchDouyinComments({ aweme_id, max_comments })        │
│                   │                                               │
│                   ▼                                              │
│           GET /douyin/web/fetch_video_comments                   │
│                   │                                               │
│                   ▼                                              │
│           comments (前5条预览)                                    │
│                  │                                               │
│                  ▼                                               │
│  handleExport()                                                   │
│       │                                                          │
│       ▼                                                          │
│  POST /tasks/comments/create_task                                 │
│       │                                                          │
│       ▼                                                          │
│  返回 task_id                                                    │
│       │                                                          │
│       ▼                                                          │
│  跳转 /download-history                                          │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DownloadHistory.vue                            │
├──────────────────────────────────────────────────────────────────┤
│  onMounted:                                                      │
│       │                                                          │
│       ▼                                                          │
│  loadAllTasks() → GET /tasks/comments/tasks                      │
│       │                                                          │
│       ▼                                                          │
│  startPolling() (每5秒)                                          │
│       │                                                          │
│       ▼                                                          │
│  对 running 状态任务:                                             │
│       │                                                          │
│       ├── pollClassificationStatus(taskId) (每5秒)               │
│       │                                                          │
│       └── GET /tasks/comments/classification_status/{taskId}    │
│                                                                   │
│  用户操作:                                                        │
│       │                                                          │
│       ├── handleDownload → GET /tasks/comments/download/{id}   │
│       │                                                          │
│       ├── handleClassify → POST /tasks/comments/classify/{id}   │
│       │                                                          │
│       └── handleDelete → DELETE /tasks/comments/tasks/{id}      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 16. 组件 Props/Emits 接口

### MainView.vue
```typescript
// Props: none
// Emits: none
// 纯展示组件，通过 router.push() 导航
```

### ParsePage.vue
```typescript
// Props: none
// Emits: none
// 布局包装组件，渲染 <VideoPreview />
```

### VideoPreview.vue
```typescript
// Props: none
// Emits: none
// 内部管理所有解析状态
```

### ExportPage.vue
```typescript
interface Props {
  platform: 'douyin' | 'tiktok'
}
// Emits: none
// 布局包装组件，渲染 <CommentExport :platform="platform" />
```

### CommentExport.vue
```typescript
interface Props {
  platform: 'douyin' | 'tiktok'
}
// Emits: none
```

### DownloadHistory.vue
```typescript
// Props: none
// Emits: none
// 内部管理任务列表和轮询
```

---

## 17. 环境变量对照表

### 前端 (.env)
| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_API_BASE_URL` | `/api` | API基础路径 |
| `VITE_USE_MOCK_DATA` | `false` | 是否启用Mock数据 |

### 后端 (config.yaml)
| 路径 | 说明 |
|------|------|
| `API.Version` | API版本号 |
| `API.Environment` | 部署环境 |
| `API.Max_Comments` | 最大评论数 |
| `Web.Max_Take_URLs` | 最大URL数 |
| `API.Download_Switch` | 下载开关 |

---

## 18. 第三方服务依赖

| 服务 | 用途 | 配置 |
|------|------|------|
| MiniMax API | AI评论分类 | `MINIMAX_API_KEY`, `OPENAI_BASE_URL` (环境变量) |
| 抖音/TikTok API | 视频/评论数据 | 无需配置，使用公共API |

---

## 19. 启动方式

### 前端开发模式
```bash
cd frontend
npm install
npm run dev    # 端口 3000
```

### 后端 (Vue SPA集成)
```bash
bash start-integrated.sh    # Vue SPA on port 8000
```

### 后端 (PyWebIO旧版)
```bash
bash start.sh               # PyWebIO on port 8000
```
