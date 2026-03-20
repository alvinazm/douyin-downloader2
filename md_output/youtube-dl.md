## youtube视频下载说明

在根目录创建了软链接将 yt-dlp 合并到 douyin-downloader2 项目中，

优点：
- 项目结构统一，看起来是一个完整的项目
- 不需要修改 youtube_crawler.py 中的导入路径
- 软链接不占用额外磁盘空间（100MB）
- yt-dlp/ 已添加到 .gitignore，不会意外提交