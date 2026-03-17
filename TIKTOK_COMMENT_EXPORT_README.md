# TikTok视频评论导出工具

## 功能介绍

这个工具允许你获取TikTok视频的评论数据并导出为CSV文件。导出的内容包含：
- 评论人
- 评论内容
- 点赞量
- 评论时间

## 使用方法

### 方法一：使用命令行工具

```bash
python3 tiktok_comment_export_tool.py <aweme_id> [max_comments] [output_file]
```

**参数说明：**
- `aweme_id`: TikTok视频作品ID（必需）
- `max_comments`: 最大评论数，默认100（可选）
- `output_file`: 输出文件路径，默认为 `download/comments/tiktok_comments_{aweme_id}.csv`（可选）

**示例：**

```bash
# 导出默认100条评论
python3 tiktok_comment_export_tool.py 7304809083817774382

# 导出500条评论
python3 tiktok_comment_export_tool.py 7304809083817774382 500

# 指定输出文件路径
python3 tiktok_comment_export_tool.py 7304809083817774382 100 /path/to/output.csv
```

### 方法二：使用API接口

启动服务器后，可以通过以下API端点导出评论：

```
GET /api/tiktok/comments/export
```

**参数说明：**
- `aweme_id`: TikTok视频作品id（必需）
- `max_comments`: 最大评论数，默认100（可选）
- `filename`: 自定义文件名（不含扩展名），默认为 `tiktok_comments_{aweme_id}`（可选）

**示例：**

```bash
# 下载评论CSV文件
curl -O "http://localhost:8000/api/tiktok/comments/export?aweme_id=7304809083817774382&max_comments=100"
```

### 方法三：使用快速启动脚本

```bash
./export_tiktok_comments.sh
```

按照提示选择操作并输入相应参数。

## 如何获取aweme_id

### 方法一：从视频URL中提取

TikTok视频URL格式示例：
- `https://www.tiktok.com/@username/video/7304809083817774382`
- `https://vm.tiktok.com/ZM6e3J8kL/`

对于长链接，直接复制最后的数字ID即可。

对于短链接，可以使用混合解析API：
```
GET /api/hybrid/video_data?url=https://vm.tiktok.com/ZM6e3J8kL/
```

返回结果中的 `video_id` 字段就是 `aweme_id`。

### 方法二：从分享信息中获取

复制TikTok APP中的分享链接，然后使用解析API获取视频ID。

## 注意事项

1. **请求频率限制**: 工具内置了0.5秒的请求间隔，避免频繁请求导致被封禁。

2. **评论数据量**: 部分热门视频可能有数千甚至数万条评论，建议使用 `max_comments` 参数限制获取的评论数量。

3. **Cookie配置**: 为了确保能正常获取评论数据，建议在配置文件中设置有效的Cookie。

4. **时间格式**: 导出的CSV文件中，时间采用 `YYYY-MM-DD HH:MM:SS` 格式。

5. **文件编码**: CSV文件使用UTF-8-BOM编码，可以在Excel中正常显示中文。

6. **地区设置**: 默认使用 US 地区设置获取评论，如需修改地区，可以编辑代码中的 `current_region` 参数。

## 文件结构

```
douyin-downloader/
├── app/
│   └── api/
│       └── endpoints/
│           └── tiktok_comment_export.py   # API端点
├── tiktok_comment_export_tool.py         # 命令行工具
├── export_tiktok_comments.sh             # 快速启动脚本
├── download/
│   └── comments/
│       └── tiktok_comments_*.csv        # 导出的CSV文件
└── TIKTOK_COMMENT_EXPORT_README.md       # 本说明文档
```

## 示例输出

CSV文件格式示例：

| 评论人 | 评论内容 | 点赞量 | 评论时间 |
|--------|----------|--------|----------|
| UserA | This video is amazing! | 123 | 2024-01-15 10:30:00 |
| UserB | Thanks for sharing | 45 | 2024-01-15 10:31:22 |

## 故障排除

### 问题1：无法获取TikTok评论数据

**解决方案：**
1. 检查Cookie是否有效
2. 检查网络连接
3. 确认aweme_id是否正确
4. 尝试不同的地区设置

### 问题2：CSV文件显示乱码

**解决方案：**
- 文件使用UTF-8-BOM编码，在Excel中应该能正常显示
- 如果在Excel中仍然乱码，可以尝试用记事本打开后另存为ANSI编码
- 或者使用支持UTF-8的软件打开，如WPS、Google Sheets等

### 问题3：无法加载服务器

**解决方案：**
1. 确保服务器正在运行：`python3 start.py`
2. 检查端口是否被占用
3. 查看日志文件：`tail -f app.log`

## 抖音 vs TikTok

这两个工具的功能几乎完全相同，主要的区别在于：

1. **数据来源**: 抖音工具从抖音平台获取数据，TikTok工具从TikTok平台获取数据
2. **API端点**:
   - 抖音: `/api/douyin/comments/export`
   - TikTok: `/api/tiktok/comments/export`
3. **文件命名**:
   - 抖音: `douyin_comments_{aweme_id}.csv`
   - TikTok: `tiktok_comments_{aweme_id}.csv`

## 许可证

Apache License 2.0
