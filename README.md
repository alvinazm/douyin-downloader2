# 启动指南

本项目现在支持两种Web前端方案：

## 方案一：PyWebIO方案（原始方案）

使用PyWebIO作为前端界面，包含完整的Web交互界面和API服务。

### 启动方式

```bash
# 方式1：使用start.sh启动（推荐）
bash start.sh

# 方式2：直接运行Python脚本
python start.py
```

### 访问地址

- **主界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

### 特点

- 原始PyWebIO界面
- 支持视频解析、批量下载
- 内置评论导出功能
- Web界面操作简单

---

## 方案二：Vue.js方案（新版方案）

使用Vue.js作为前端界面，配合FastAPI提供更好的用户体验和现代化界面。

### 启动方式

```bash
# 使用集成启动脚本
bash start-integrated.sh
```

### 启动选项

脚本会显示以下选项：

1. **后端 + 前端生产模式**（推荐）
   - 使用已构建的Vue前端
   - 访问：http://localhost:8000

2. **后端 + 前端开发模式**
   - 前端开发服务器：http://localhost:3000
   - 后端API：http://localhost:8000
   - 需要安装Node.js

3. **仅启动后端**
   - 使用已构建的Vue前端
   - 访问：http://localhost:8000

4. **仅启动前端开发模式**
   - 前端开发服务器：http://localhost:3000
   - 需要后端API在8000端口运行
   - 需要安装Node.js

### 访问地址

- **主界面**（生产模式）：http://localhost:8000
- **主界面**（开发模式）：http://localhost:3000
- **PyWebIO旧界面**：http://localhost:8000/pywebio
- **API文档**：http://localhost:8000/docs
- **ReDoc文档**：http://localhost:8000/redoc

### 特点

- 现代化Vue.js界面
- 更好的用户体验
- 单页应用（SPA）
- 支持前端开发模式（热更新）
- 保留了PyWebIO兼容性（/pywebio路由）

---

## 快速对比

| 特性 | PyWebIO方案 | Vue.js方案 |
|------|-------------|------------|
| 启动命令 | `bash start.sh` | `bash start-integrated.sh` |
| 前端技术 | PyWebIO | Vue.js |
| 开发模式 | 不支持 | 支持 |
| 用户界面 | 传统风格 | 现代化 |
| 移动端适配 | 基础 | 更好 |
| 安装依赖 | 仅Python | Python + Node.js（仅开发模式） |

---

## 配置说明

两个方案共享相同的配置文件 `config.yaml`：

```yaml
# Web配置
Web:
  PyWebIO_Enable: true    # 启用PyWebIO功能（Vue方案下通过/pywebio访问）

# API配置
API:
  Host_IP: 0.0.0.0        # 监听地址
  Host_Port: 8000         # 监听端口
  Docs_URL: /docs         # Swagger文档路径
```

---

## 常见问题

### 1. 选择哪个方案？

- **新手用户**：推荐使用PyWebIO方案（start.sh），简单易用
- **开发者**：推荐使用Vue.js方案（start-integrated.sh），支持开发模式
- **生产环境**：推荐使用Vue.js生产模式

### 2. 同时运行两个方案？

不可以同时运行，因为都使用8000端口。需要先停止一个再启动另一个。

### 3. 如何停止服务？

```bash
# 停止PyWebIO方案
pkill -f "python start.py"

# 停止Vue.js方案
pkill -f "uvicorn app.vue_main:app"
```

### 4. Vue前端找不到？

确保 `frontend/dist` 目录存在，如果没有需要先构建：

```bash
cd frontend
npm install
npm run build
```

---

## 文件结构

```
douyin-downloader/
├── app/
│   ├── main.py           # PyWebIO方案入口
│   └── vue_main.py       # Vue.js方案入口
├── frontend/             # Vue前端代码
│   └── dist/             # 构建后的前端文件
├── start.sh              # PyWebIO方案启动脚本
└── start-integrated.sh   # Vue.js方案启动脚本
```


### 5. 导出数量配置

配置在：config.yaml
Max_Take_URLs: 30    # Maximum number of URLs that can be taken at a time | 一次最多可以取得的URL数量
Max_Comments: 50000    # Maximum number of comments to export | 最大评论导出数量

####   Environment: Demo 的作用

Environment: Demo 表示当前运行环境的类型，主要作用是：
配置说明
API:
  Environment: Demo    # 可以是 "Demo"、"Production"、"Development" 等
作用
1. 标识运行环境
- Demo - 演示/测试环境
- Production - 生产环境
- Development - 开发环境

2. 后端用途
- 在 API 文档（/docs）中显示当前环境
- API 响应中包含环境信息
- 便于区分不同的部署环境

3. 前端用途（stores/config.ts）
const isProduction = computed(() => environment.value === 'Production')
const isDemo = computed(() => environment.value === 'Demo')
- isProduction - 判断是否为生产环境
- isDemo - 判断是否为演示环境
- 在"关于"页面显示当前环境

4. 可能的扩展用途
- 根据环境启用/禁用某些功能
- 不同环境使用不同的日志级别
- 统计和监控的区分
注意： 目前代码中主要用于显示和标识，没有实际改变应用行为。你可以根据需要在不同环境下添加不同的逻辑。

# 日志

- server.log 是服务器启动日志，也记录了视频解析、下载结果，可以作为备份日志；
- logs/parser_video_2026-03-25.log 是视频解析日志
- logs/download_video_2026-03-25.log 是视频下载日志