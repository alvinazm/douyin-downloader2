#!/bin/sh

# 读取配置文件获取端口号
PORT=$(grep -oP '(?<=Host_Port: )\S+' config.yaml)

# 停止占用${PORT}端口的进程
echo "停止占用${PORT}端口的进程..."
lsof -ti:${PORT} | xargs kill -9 2>/dev/null || echo "没有进程占用${PORT}端口"

# 等待端口释放
sleep 1

# Starting the Python application directly using python3
python3 start.py
