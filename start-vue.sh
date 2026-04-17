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

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${bash_source[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 设置虚拟环境路径
VENV_DIR="$SCRIPT_DIR/venv"

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 安装依赖（如果需要）
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "检查/安装Python依赖..."
    pip install -q --upgrade pip
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
fi

echo ""
echo "虚拟环境已激活: $VENV_DIR"
echo "启动后端服务器 + Vue前端生产模式..."
echo ""
echo "服务将在以下地址可用:"
echo "  - 主页: http://localhost:4040"
echo "  - API文档: http://localhost:4040/docs"
echo "  - WebHook回调地址: http://localhost:4040/api/hybrid/update_cookie"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${bash_source[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 停止占用4040端口的进程
echo "停止占用4040端口的进程..."
lsof -ti:4040 | xargs kill -9 2>/dev/null || echo "没有进程占用4040端口"

# 等待端口释放
sleep 1

# 安装前端依赖
echo "安装前端依赖..."
cd frontend && npm install && npm run build && cd ..

# 设置PYTHONPATH
export PYTHONPATH="$(pwd):${PYTHONPATH}"

# 启动服务器并配置日志
mkdir -p logs
uvicorn app.vue_main:app --host 0.0.0.0 --port 4040 --reload 2>&1 | tee -a server.log
