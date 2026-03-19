# 小工具 UI 视觉规范

## 设计原则

### 核心理念
**「专业实用主义」** - 为功能导向的实用工具打造专业、高效、现代化的界面风格

这一美学方向融合了工业设计的实用性与现代数字产品的精致感，强调：

- **功能优先**：设计服务于功能，无多余装饰
- **专业性**：传递可靠、可信的工具形象
- **现代感**：避免过时的工具感，保持当代审美
- **一致性**：所有组件和功能遵循统一的设计语言，禁止为不同功能使用不同颜色

---

## 颜色统一性原则（核心规则）

### ⚠️ 严禁违反的颜色规则

#### 禁止的行为
1. **禁止为不同功能使用不同颜色**
   - ❌ 错误：抖音用紫色、TikTok用粉色、视频用蓝色
   - ✅ 正确：所有操作按钮统一使用蓝色渐变

2. **禁止混用多种渐变色**
   - ❌ 错误：紫色系、粉色系、红色系、橙色系、绿色系混用
   - ✅ 正确：蓝色系统一所有操作按钮

3. **禁止根据平台差异改变主色调**
   - ❌ 错误：抖音用紫色、TikTok用粉色
   - ✅ 正确：所有平台统一使用蓝色

4. **禁止深色按钮与蓝色按钮混用**
   - ❌ 错误：有些按钮用深灰色、有些用蓝色
   - ✅ 正确：所有主要操作按钮统一使用蓝色

#### 允许的特殊颜色使用场景

以下场景**允许**使用其他颜色，但必须严格控制：

| 场景 | 允许颜色 | 使用规则 |
|------|---------|---------|
| **状态提示** | 成功绿、错误红、警告黄 | 仅用于结果显示，不可用于按钮 |
| **加载动画** | 蓝色旋转 | 统一使用蓝色 |
| **功能卡片标签** | 蓝色渐变 | 所有卡片标签统一使用蓝色 |
| **图标装饰** | 继承文本颜色 | 保持与文本颜色一致 |

---

## 色彩系统

### 主色调（基于实际应用）
```css
--primary: #0F172A;        /* 深蓝灰 - 专业信赖 */
--primary-light: #1E293B;  /* 浅一度的深蓝灰 */
--primary-dark: #020617;   /* 最深色 */

--accent: #3B82F6;         /* 活力蓝 - 点缀与交互 */
--accent-hover: #2563EB;   /* 悬停状态 */
--accent-subtle: #DBEAFE;  /* 柔和蓝 - 背景/标签 */
```

### 中性色
```css
--neutral-900: #111827;    /* 最深文字 */
--neutral-800: #1F2937;    /* 深色文字 */
--neutral-700: #374151;    /* 次深文字 */
--neutral-600: #4B5563;    /* 中等文字 */
--neutral-500: #6B7280;    /* 中浅文字 */
--neutral-400: #9CA3AF;    /* 浅色文字 */
--neutral-300: #D1D5DB;    /* 边框线 */
--neutral-200: #E5E7EB;    /* 浅边框/分割线 */
--neutral-100: #F3F4F6;    /* 极浅背景 */
--neutral-50: #F9FAFB;     /* 更浅背景 */
```

### 语义色（仅用于状态提示）
```css
/* 成功 */
--success: #10B981;
--success-bg: #D1FAE5;

/* 警告 */
--warning: #F59E0B;
--warning-bg: #FEF3C7;

/* 错误 */
--error: #EF4444;
--error-bg: #FEE2E2;

/* 信息 */
--info: #3B82F6;
--info-bg: #DBEAFE;
```

### 背景色
```css
--bg-primary: #FFFFFF;     /* 主背景白 */
--bg-secondary: #F3F4F6;   /* 次要背景灰（页面背景） */
--bg-tertiary: #F9FAFB;    /* 第三背景轻灰 */
--bg-elevated: #FFFFFF;    /* 抬升元素背景 */
--bg-overlay: rgba(0, 0, 0, 0.4); /* 遮罩层 */
```

### 标准渐变色（严格限制）

#### 操作按钮渐变（唯一允许的按钮渐变）
```css
/* 主要操作按钮 - 蓝色渐变 */
from-blue-500 to-blue-600
hover:from-blue-600 hover:to-blue-700
```

#### 背景区域渐变（仅用于装饰性区域）
```css
/* 轻量装饰背景 */
from-blue-50 to-blue-50  /* 单色渐变 */
bg-blue-50              /* 纯色背景 */
```

#### 禁止的渐变色（不要使用）
```css
/* ❌ 禁止使用的渐变色 */
from-purple-500 to-purple-600    /* 紫色系 */
from-pink-500 to-pink-600        /* 粉色系 */
from-rose-500 to-rose-600        /* 红色系 */
from-orange-500 to-orange-600    /* 橙色系 */
from-emerald-500 to-emerald-600  /* 绿色系 */
from-blue-50 to-purple-50        /* 混合渐变 */
```

---

## 核心组件严格样式规范

### 1. 按钮组件（必须严格遵守）

#### 🟦 主要操作按钮（所有页面统一）
**用途**：提交、确认、执行、导出等主要操作

```vue
<!-- 完整代码 -->
<button class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
  操作文本
</button>

<!-- 标准化样式类 -->
class基础: px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium
hover: hover:from-blue-600 hover:to-blue-700 transition-all duration-200
disabled: disabled:opacity-50 disabled:cursor-not-allowed
```

**禁止使用**：
- ❌ `from-purple-500 to-purple-600`
- ❌ `from-pink-500 to-pink-600`
- ❌ `from-rose-500 to-rose-600`
- ❌ `from-orange-500 to-orange-600`
- ❌ `from-emerald-500 to-emerald-600`
- ❌ `bg-gray-800`（深色按钮）

#### ⚪ 次要操作按钮
**用途**：返回、取消、重置、次要导航

```vue
<!-- 方案1：白底灰边（推荐用于返回按钮） -->
<button class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-lg font-medium shadow-sm hover:shadow-md hover:text-blue-600 transition-all duration-200">
  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
  </svg>
  返回
</button>

<!-- 方案2：灰色背景（推荐用于重置按钮） -->
<button class="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
  重置
</button>
```

**禁止使用**：
- ❌ 任何彩色渐变
- ❌ 深色背景 `bg-gray-800`
- ❌ 与主按钮颜色不同的渐变

#### 🔵 幽灵按钮
**用途**：辅助操作、链接样式

```vue
<button class="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-all duration-200">
  操作
</button>
```

### 2. 输入框组件

```vue
<!-- 文本输入框 -->
<input 
  type="text"
  class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
  placeholder="请输入..."
/>

<!-- 文本域 -->
<textarea
  class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
  placeholder="请输入..."
></textarea>
```

**关键样式**：
- 背景：`bg-white`
- 边框：`border border-gray-300`
- 聚焦：`focus:ring-2 focus:ring-blue-500`
- 过渡：`transition-all duration-200`

### 3. 功能卡片组件

```vue
<button class="group relative bg-white border-2 border-gray-200 hover:border-blue-500 rounded-xl p-6 text-left shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
  <div class="flex items-start justify-between mb-3">
    <span class="text-3xl">🔍</span>
    <div class="px-2.5 py-1 text-xs font-medium text-white rounded-full bg-gradient-to-r from-blue-500 to-blue-600">
      新功能
    </div>
  </div>
  <h3 class="text-lg font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
    功能标题
  </h3>
  <p class="text-sm text-gray-500">
    功能描述文本
  </p>
  <div class="mt-4 pt-4 border-t border-gray-200 flex items-center text-sm text-blue-600 font-medium">
    立即使用
    <svg class="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
    </svg>
  </div>
</button>
```

**关键样式**：
- 背景：`bg-white`
- 边框：`border-2 border-gray-200`
- hover：`hover:border-blue-500 hover:shadow-xl hover:-translate-y-1`
- 标签：`bg-gradient-to-r from-blue-500 to-blue-600`（必须蓝色）

**禁止使用**：
- ❌ 任何非蓝色的标签渐变
- ❌ 不同卡片使用不同颜色标签

### 4. 结果卡片组件

```vue
<div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md transition-all duration-200">
  <div class="flex items-center gap-3 mb-4">
    <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-green-500">
      <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm text-gray-900 break-all font-medium">结果标题</div>
    </div>
  </div>
  
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-3 text-sm">
      <div class="flex flex-col">
        <span class="text-gray-500 mb-1">字段名</span>
        <span class="text-gray-900 font-medium">字段值</span>
      </div>
    </div>
    
    <div class="flex flex-wrap gap-2">
      <a
        href="#"
        target="_blank"
        class="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 transition-all duration-200"
      >
        无水印 (高清)
      </a>
      <a
        href="#"
        target="_blank"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-all duration-200"
      >
        有水印 (高清)
      </a>
    </div>
  </div>
</div>
```

**关键样式**：
- 背景：`bg-white`
- 边框：`border-2 border-gray-200`
- 阴影：`shadow-md`
- 操作链接：`bg-green-500`和 `bg-blue-500`（允许不同，表示不同状态）

### 5. 模态框组件

```vue
<Transition 
  enter-active-class="transition-all duration-300 ease-out"
  enter-from-class="opacity-0 scale-95"
  enter-to-class="opacity-100 scale-100"
  leave-active-class="transition-all duration-200 ease-in"
  leave-from-class="opacity-100 scale-100"
  leave-to-class="opacity-0 scale-95"
>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
    <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
      
      <!-- 模态框头部 -->
      <div class="flex items-center justify-between p-5 border-b border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900">标题</h3>
        <button 
          @click="close"
          class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      
      <!-- 模态框内容 -->
      <div class="p-6 overflow-y-auto max-h-[60vh]">
        <!-- 内容 -->
      </div>
      
    </div>
  </div>
</Transition>
```

**关键样式**：
- 背景：`bg-white`
- 边框圆角：`rounded-2xl`
- 阴影：`shadow-2xl`
- 遮罩：`bg-black/40 backdrop-blur-sm`

### 6. 状态提示组件

#### 加载状态
```vue
<div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
  <div class="flex items-center gap-3 text-blue-700">
    <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <div>加载中...</div>
  </div>
</div>
```

#### 错误状态
```vue
<div class="p-4 bg-red-50 border border-red-200 rounded-lg">
  <div class="flex items-center gap-3 text-red-700">
    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>
    <div>错误信息</div>
  </div>
</div>
```

#### 成功状态
```vue
<div class="p-4 bg-green-50 border border-green-200 rounded-lg">
  <div class="flex items-center gap-3 text-green-700">
    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
    </svg>
    <div>成功信息</div>
  </div>
</div>
```

---

## 页面结构规范

### 首页结构（MainView.vue）
```vue
<div class="min-h-screen bg-gray-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- 头部区域 -->
    <header class="text-center mb-12">
      <div class="inline-flex items-center justify-center mb-6">
        <img class="w-20 h-20 rounded-2xl shadow-lg" />
      </div>
      <h1 class="text-4xl font-bold text-gray-900 mb-3">标题</h1>
      <p class="text-lg text-gray-600 max-w-2xl mx-auto mb-8">描述</p>
      
      <!-- 导航按钮组（次要按钮） -->
      <nav class="inline-flex items-center gap-3 flex-wrap justify-center">
        <button class="px-5 py-2.5 bg-white text-gray-700 rounded-lg font-medium shadow-sm hover:shadow-md hover:text-blue-600 transition-all duration-200">
          按钮文本
        </button>
      </nav>
    </header>

    <!-- 主内容区域 -->
    <main>
      <!-- 功能卡片网格 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 功能卡片（所有标签使用蓝色渐变） -->
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="mt-16 text-center text-sm text-gray-500">
      版权信息
    </footer>

  </div>
</div>
```

### 功能页面结构（ParsePage.vue, ExportPage.vue）
```vue
<div class="min-h-screen bg-gray-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- 头部区域 -->
    <header class="mb-8">
      <!-- 返回按钮（次要按钮） -->
      <button class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-lg font-medium shadow-sm hover:shadow-md hover:text-blue-600 transition-all duration-200">
        返回主页
      </button>
    </header>

    <!-- 主内容区域 -->
    <main>
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">页面标题</h1>
        <p class="text-gray-600">页面描述</p>
      </div>
      
      <!-- 内容卡片 -->
      <div class="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-md">
        <!-- 内容 -->
        
        <!-- 主要操作按钮（蓝色渐变） -->
        <button class="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200">
          操作
        </button>
      </div>
    </main>

  </div>
</div>
```

---

## 响应式设计

### 断点
```css
--breakpoint-sm: 640px;   /* 默认 - 手机竖屏 */
--breakpoint-md: 768px;   /* 平板 */
--breakpoint-lg: 1024px;  /* 桌面 */
--breakpoint-xl: 1280px;  /* 大屏桌面 */
```

响应式类应用：
```css
px-4 sm:px-6 lg:px-8          /* 内边距响应式 */
grid-cols-1 sm:grid-cols-2     /* 网格列数响应式 */
```

---

## 检查清单（开发前必读）

### 新页面开发检查清单
- [ ] 所有主要操作按钮使用蓝色渐变 `from-blue-500 to-blue-600`
- [ ] 所有次要操作按钮使用 `bg-white` 或 `bg-gray-100`
- [ ] 所有卡片标签使用蓝色渐变
- [ ] 没有使用紫色、粉色、红色、橙色、绿色作为按钮颜色
- [ ] 没有使用深色按钮 `bg-gray-800`
- [ ] 所有输入框使用 `bg-white` 和 `border-gray-300`
- [ ] 所有卡片使用 `bg-white` 和 `border-gray-200`
- [ ] 页面背景使用 `bg-gray-100`

### 代码审查检查清单
- [ ] 是否存在为不同功能使用不同颜色的按钮？
- [ ] 是否存在非蓝色渐变的按钮？
- [ ] 是否存在与规范不一致的深色按钮？
- [ ] 是否所有加载/错误/成功状态使用正确的颜色？
- [ ] 是否所有焦点状态可见且一致？

---

## 附录

### 技术栈
- **CSS 框架**：Tailwind CSS 3.4+
- **构建工具**：Vite 5.0+
- **Vue**：Vue 3.4+
- **图标**：Heroicons

### 工具参考
- Tailwind CSS 文档：https://tailwindcss.com/docs
- 可访问性检查：axe DevTools
- 对比度检查：WebAIM Contrast Checker

---

*本规范是项目开发强制执行的标准，任何违反颜色统一性的代码将被打回重写。如有疑问，请先与设计团队确认。*
