# Douyin-TikTok 下载器前端项目

基于 Vue 3 + TypeScript + Tailwind CSS 开发的现代化前端应用，用于解析和下载抖音、TikTok、Bilibili 的视频和图集。

## 技术栈

- **框架**: Vue 3 (SFC + Composition API)
- **构建工具**: Vite
- **语言**: TypeScript (严格模式)
- **样式**: Tailwind CSS (原子化CSS)
- **状态管理**: Pinia
- **HTTP客户端**: Axios (已封装拦截器)

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   │   └── mock-data/   # Mock数据
│   ├── api/             # API封装
│   │   └── index.ts     # ApiClient类
│   ├── components/      # Vue组件
│   │   ├── MainView.vue # 主界面
│   │   ├── VideoPreview.vue # 视频解析
│   │   └── CommentExport.vue # 评论导出
│   ├── composables/     # 组合式函数
│   │   ├── useVideoParser.ts
│   │   ├── useDownloader.ts
│   │   ├── useCommentExporter.ts
│   │   └── useToast.ts
│   ├── stores/          # Pinia状态管理
│   │   ├── config.ts    # 配置状态
│   │   └── parser.ts    # 解析器状态
│   ├── types/           # TypeScript类型定义
│   │   ├── api.ts
│   │   └── video.ts
│   ├── utils/           # 工具函数
│   │   └── url.ts       # URL工具
│   ├── App.vue          # 根组件
│   ├── main.ts          # 入口文件
│   └── style.css        # 全局样式
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:3000`

### 构建生产版本

```bash
npm run build
```

### 类型检查

```bash
npm run type-check
```

## 开发规范

### 组件开发

- 使用 `<script setup lang="ts">` 语法
- 组件命名使用 PascalCase
- 超过200行的组件，将逻辑抽离到 `composables`

### 样式规范

- 优先使用 Tailwind CSS 原子类
- 排列顺序: 定位 -> 布局 -> 间距 -> 尺寸 -> 视觉
- 动态Class使用对象语法

### TypeScript规范

- 优先使用 `ref()`
- 复杂对象使用 `reactive()`
- 强类型定义，禁止过度使用 `any`

### API调用

- 所有API调用统一使用 `src/api/index.ts` 中的 `ApiClient` 类
- 使用Mock数据进行开发测试

## 功能特性

### 1. 批量视频解析
- 支持抖音、TikTok、Bilibili混合解析
- 实时显示解析进度
- 支持无水印/有水印版本下载

### 2. 评论导出
- 导出抖音/TikTok评论到CSV
- 支持通过ID或URL导出
- 可控制导出数量

### 3. 响应式设计
- 移动端友好
- 现代化磨砂玻璃UI

## Mock数据使用

在开发环境中，可以使用Mock数据进行演示：

```typescript
const useMock = true
await parseMultipleUrls(urls, useMock)
```

## API配置

开发环境下，API请求会代理到 `http://localhost:8000`。

如需修改，编辑 `.env` 文件：

```env
VITE_API_BASE_URL=/api
```

## 注意事项

1. **Cookie配置**: 部署后需要替换相应的Cookie到后端配置文件
2. **并发控制**: 批量下载已实现串行处理，防止触发风控
3. **错误处理**: 所有网络请求都有完善的错误处理
4. **类型安全**: 所有API返回都有完整的TypeScript类型定义
