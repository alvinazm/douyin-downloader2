# 快速启动指南

## 方法1: 使用启动脚本(推荐)

在项目根目录运行:

### PyWebIO方案（原始）

```bash
bash start.sh
```

### Vue.js方案（新版）

```bash
bash start-integrated.sh
```

访问地址: http://localhost:8000

## 访问地址

- **生产模式**: http://localhost:8000
- **开发模式**:
  - 前端: http://localhost:3000
  - 后端API: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **PyWebIO旧界面**: http://localhost:8000/pywebio

## 常见问题

### 1. 前端无法连接后端

- 检查后端是否在8000端口运行
- 检查浏览器控制台Network请求

### 2. API请求失败

- 检查Cookie配置
- 查看后端日志
- 某些平台可能需要代理/VPN

### 3. 重新构建前端

```bash
cd frontend
npm run build
```

详细文档请查看 `FRONTEND_INTEGRATION.md`
