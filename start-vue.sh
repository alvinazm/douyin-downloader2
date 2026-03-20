#!/bin/bash

echo "=========================================="
echo "  Douyin TikTok Download API"
echo "  Vue.js方案启动脚本"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3 未安装或不在PATH中"
    exit 1
fi

echo "启动后端服务器 + Vue前端生产模式..."
echo ""
echo "服务将在以下地址可用:"
echo "  - 主页: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo "  - PyWebIO: http://localhost:8000/pywebio"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${bash_source[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 停止占用8000端口的进程
echo "停止占用8000端口的进程..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "没有进程占用8000端口"

# 等待端口释放
sleep 1

# 构建前端
echo "构建前端..."
cd frontend && npm run build && cd ..

# 设置PYTHONPATH
export PYTHONPATH="$(pwd):${PYTHONPATH}"

python3 -m uvicorn app.vue_main:app --host 0.0.0.0 --port 8000 --reload
