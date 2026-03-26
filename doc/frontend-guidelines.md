# 前端开发规范指引 (frontend-guidelines.md)

> **目标**：将 `alvinazm/douyin-downloader` 重构为现代 Vue 3 生态架构，确保代码高可维护性、类型安全及性能最优。

---

## 1. 核心技术栈 (Tech Stack)
* **框架**: Vue 3 (SFC) 使用 `<script setup>` 语法。
* **构建工具**: Vite (追求极致的开发与构建速度)。
* **路由管理**: Vue Router 4 (官方路由解决方案，支持基于文件的路由)。
* **状态管理**: Pinia (替代 Vuex，支持模块化状态管理)。
* **样式方案**: Tailwind CSS (原子化 CSS，禁止随意编写原生 `.css` 或 `.scss`)。
* **类型检查**: TypeScript (严格模式，禁止过度使用 `any`)。
* **网络请求**: Axios (需封装拦截器，处理抖音解析的特殊 Headers)。

---

## 2. 路由系统规范 (Vue Router)
### 2.1 路由配置
* **路由文件**: 所有路由配置统一存放在 `src/router` 目录下，按模块拆分，推荐使用 `index.ts` 作为主入口。
* **路由定义**: 使用 `createRouter` 动态导入路由配置，支持懒加载：
    ```typescript
    const routes = [
      {
        path: '/',
        component: () => import('@/views/HomeView.vue'),
        name: 'home'
      },
      {
        path: '/download',
        component: () => import('@/views/DownloadView.vue'),
        name: 'download'
      }
    ]
    ```
* **History 模式**: 生产环境必须使用 `createWebHistory` 模式，开发环境可使用 `createWebHashHistory` 避免服务器配置问题。

### 2.2 导航守卫
* **全局守卫**: 在 `src/router/index.ts` 中配置全局前置守卫 `router.beforeEach`，处理登录状态、权限控制等。
* **路由元信息**: 为路由添加 `meta` 字段，定义页面标题、权限要求、是否需要登录等元数据：
    ```typescript
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      meta: { title: '设置', requiresAuth: true }
    }
    ```
* **离开守卫**: 对于有表单编辑或未保存数据的页面，必须使用 `onBeforeRouteLeave` 防止误操作导致数据丢失。

### 2.3 路由导航
* **编程式导航**: 使用 `useRouter` 和 `useRoute` 组合式 API 进行路由操作：
    ```typescript
    const router = useRouter()
    const route = useRoute()
    router.push({ name: 'home', query: { id: '123' } })
    console.log(route.query.id)
    ```
* **声明式导航**: 在模板中使用 `<RouterLink />` 组件替代 `<a>` 标签，自动处理激活状态。

### 2.4 路由懒加载
* **代码分割**: 对非核心页面（如设置页、历史记录页等）使用动态导入实现路由懒加载，优化首屏加载性能。
* **加载状态**: 为懒加载页面配置全局加载动画，提升用户体验。

---

## 3. 组件开发规范 (Component Standards)
### 2.1 命名与结构
* **文件名**: 始终使用大驼峰命名法 (PascalCase)，如 `VideoPreview.vue`, `SettingsPanel.vue`。
* **组件顺序**:
    1. `<script setup lang="ts">`：逻辑层。
    2. `<template>`：视图层。
    3. `<style scoped>`：仅用于处理无法由 Tailwind 实现的特殊样式。
* **逻辑抽离**: 超过 **200 行** 的组件，必须将非 UI 逻辑（如：视频解析算法、下载进度计算）抽离到 `src/composables` 文件夹中。

### 2.2 响应式约定
* **基本类型**: 优先使用 `ref()`。
* **复杂对象**: 仅在处理表单数据或高度关联的配置对象时使用 `reactive()`。
* **解构防护**: 在组件中从 Store 或 Props 解构数据时，必须使用 `toRefs()` 或 `storeToRefs()` 以保持响应式。

---

## 4. Tailwind CSS 使用规范
* **原子优先**: 严禁在组件内部定义大量局部 CSS。优先使用 Tailwind 预设。
* **排列顺序**: 定位 (absolute/relative) -> 布局 (flex/grid) -> 间距 (m/p) -> 尺寸 (w/h) -> 视觉 (bg/text/rounded)。
* **动态 Class**: 推荐使用对象语法处理动态样式：
    ```vue
    <div :class="{ 'opacity-50': isLoading, 'bg-blue-500': !isLoading }"></div>
    ```

---

## 5. 业务逻辑与安全 (抖音下载器专项)
* **API 封装**: 所有针对抖音解析接口的调用，必须统一存放在 `src/api` 目录下，并定义完整的 `interface` 描述返回数据。
* **并发控制**: 批量下载任务必须实现并发限制（如使用 `p-limit`），防止请求过快触发风控。
* **错误捕获**: 
    * 解析失败、链接无效、网络超时必须有对应的 **Toast** 或 **Dialog** 提示。
    * 使用 `try-catch` 包裹所有异步下载逻辑。
* **数据持久化**: 用户的下载记录、API 偏好设置需通过 Pinia 的插件持久化到 `localStorage`。

---

## 6. TypeScript 规范
* **定义优先**: 严禁在不定义类型的情况下直接处理解析出的 JSON 数据。
* **Props 声明**: 强制使用 `defineProps<{ ... }>()` 进行宏声明，增强 IDE 提示。
* **枚举使用**: 对于“下载状态（等待中/下载中/已完成/失败）”，必须使用 `enum` 进行定义。

---

## 7. AI 重写协作指令 (给 AI 的特别提醒)
1.  **代码转换**: 当你看到原项目中的 `jQuery` 操作或 `getElementById` 时，请将其重写为 Vue 的 `ref` 绑定。
2.  **模块化**: 不要把解析逻辑直接写在 `.vue` 文件里。请在 `src/utils` 或 `src/composables` 中实现，并保持函数纯粹性。
3.  **注释要求**: 所有的核心解析函数（涉及 Token、Signature 或正则提取的部分）必须保留详细的注释，说明原逻辑的意图。
4.  **防范幻觉**: 如果原代码中某些抖音 API 的字段已失效或不明确，请标注 `[DEPRECATED]` 并优先采用你知识库中最新的解析思路。

---