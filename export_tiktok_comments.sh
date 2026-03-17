#!/bin/bash
# TikTok评论导出工具快速启动脚本

echo "========================================="
echo "  TikTok视频评论导出工具"
echo "========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装"
    exit 1
fi

echo "检查依赖..."
python3 -c "import aiofiles, httpx, yaml, fastapi, starlette" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装依赖中..."
    pip3 install -r requirements.txt
fi

echo ""
echo "请选择操作："
echo "1. 下载指定TikTok视频的评论"
echo "2. 启动API服务器"
echo "3. 查看使用说明"
echo "4. 退出"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        read -p "请输入TikTok视频ID (aweme_id): " aweme_id
        read -p "请输入最大评论数 (默认100): " max_count
        
        if [ -z "$max_count" ]; then
            max_count=100
        fi
        
        echo ""
        echo "开始下载TikTok评论..."
        python3 tiktok_comment_export_tool.py $aweme_id $max_count
        ;;
    2)
        echo ""
        echo "启动API服务器..."
        python3 start.py
        ;;
    3)
        echo ""
        echo "使用说明："
        echo "1. 使用方式1：命令行工具"
        echo "   python3 tiktok_comment_export_tool.py <aweme_id> [max_comments]"
        echo "   示例: python3 tiktok_comment_export_tool.py 7304809083817774382 100"
        echo ""
        echo "2. 使用方式2：API服务"
        echo "   启动服务后访问: http://localhost:8000/docs"
        echo "   API endpoint: GET /tiktok/comments/export"
        echo "   参数: aweme_id, max_comments (可选), filename (可选)"
        echo ""
        echo "3. 导出文件位置："
        echo "   download/comments/tiktok_comments_{aweme_id}.csv"
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
