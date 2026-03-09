# 抖音评论导出 - 快速使用示例

## 🎯 5分钟快速开始

### 示例1: 通过Web界面导出评论（最简单）

**步骤：**
1. 打开浏览器，访问：http://localhost:8000
2. 在菜单中选择："💬导出视频评论 (通过ID)"
3. 输入视频ID：`7372484719365098803`
4. 设置最大评论数：`50`（可选，默认100）
5. 点击"提交"按钮
6. 等待评论获取完成
7. 点击"下载CSV文件"按钮

**结果：**
会得到文件：`douyin_comments_7372484719365098803.csv`

### 示例2: 通过命令行导出评论

```bash
cd /Users/azm/MyProject/douyin-downloader

# 导出100条评论
python3 comment_export_tool.py 7372484719365098803 100

# 导出50条评论到指定文件
python3 comment_export_tool.py 7372484719365098803 50 /tmp/my_comments.csv
```

### 示例3: 通过API接口导出评论

```bash
# 使用curl直接下载
curl -O "http://localhost:8000/api/douyin/comments/export?aweme_id=7372484719365098803&max_comments=50"

# 下载并重命名文件
curl -o my_video_comments.csv "http://localhost:8000/api/douyin/comments/export?aweme_id=7372484719365098803&max_comments=50"
```

### 示例4: 解析视频后直接导出评论

**步骤：**
1. 访问：http://localhost:8000
2. 选择："🔍批量解析视频"
3. 粘贴抖音视频链接：`https://www.douyin.com/video/7372484719365098803`
4. 点击"提交"解析视频
5. 在解析结果页面找到："下载评论CSV"
6. 点击即可下载该视频的评论

## 📊 数据格式示例

### 导出的CSV文件内容示例：

```csv
评论人,评论内容,点赞量,评论时间
用户3875812886417,宝宝我秒回  点评吱声[色],9,1970-01-21 04:56:22
11.16⁻,宝宝我点巨快 点了吱[猪头],17,1970-01-21 05:07:42
王先生看心理,应该配，许嵩的天龙八部那首歌,1,1970-01-21 20:21:45
```

### 在Excel中打开：

1. 双击CSV文件，Excel自动打开
2. 如果显示乱码：
   - 数据 → 获取数据 → 从文本/CSV
   - 选择文件
   - 文件原始格式：UTF-8
   - 点击加载

## 🔄 批量处理示例

### 批量导出多个视频的评论

创建脚本 `batch_export.sh`：

```bash
#!/bin/bash

# 视频ID列表
VIDEO_IDS=(
    "7372484719365098803"
    "7380000000000000000"
    "7390000000000000000"
)

# 循环导出
for video_id in "${VIDEO_IDS[@]}"
do
    echo "正在处理视频: $video_id"
    python3 comment_export_tool.py $video_id 100
    echo "完成: $video_id"
    echo "---"
done

echo "全部完成！"
```

运行：
```bash
chmod +x batch_export.sh
./batch_export.sh
```

### 批量合并CSV文件

```python
import pandas as pd
import glob

# 读取所有CSV文件
all_files = glob.glob("download/comments/*.csv")
df_list = []

for filename in all_files:
    df = pd.read_csv(filename)
    df['source_file'] = filename  # 添加来源信息
    df_list.append(df)

# 合并所有文件
merged_df = pd.concat(df_list, ignore_index=True)

# 保存合并后的文件
merged_df.to_csv("all_comments_merged.csv", index=False, encoding='utf-8-sig')
print(f"合并完成！共 {len(merged_df)} 条评论")
```

## 💡 高级用法

### 自定义CSV格式

修改 `app/api/endpoints/comment_export.py` 中的字段：

```python
# 添加更多字段
fieldnames = ['评论人', '评论内容', '点赞量', '评论时间', '评论ID', '用户ID']
```

### 定时导出评论

使用cron定时任务：

```bash
# 编辑定时任务
crontab -e

# 每天凌晨2点导出评论
0 2 * * * cd /Users/azm/MyProject/douyin-downloader && python3 comment_export_tool.py 7372484719365098803 100
```

### 数据分析示例

```python
import pandas as pd

# 读取CSV
df = pd.read_csv('douyin_comments_7372484719365098803.csv')

# 统计点赞最高的10条评论
top_comments = df.nlargest(10, '点赞量')
print(top_comments[['评论人', '评论内容', '点赞量']])

# 统计评论最多的用户
top_users = df['评论人'].value_counts().head(10)
print(top_users)
```

## ❓ 常见问题

### Q1: 如何获取视频ID？

**A:** 
- 从视频URL提取：`https://www.douyin.com/video/7372484719365098803`
- 使用解析功能：选择"💬导出视频评论 (通过URL)"，系统会自动解析

### Q2: 最多能导出多少条评论？

**A:** 
- 理论上无限制
- 建议单次不超过500-1000条
- 大量评论需要较长时间

### Q3: 导出的时间显示不对怎么办？

**A:** 
- 这是已知问题，不影响其他数据
- 可以在Excel中手动调整时间格式

### Q4: 可以导出TikTok或Bilibili的评论吗？

**A:** 
- 当前版本仅支持抖音
- 未来版本可能会添加对其他平台的支持

## 📞 获取帮助

- 📖 详细文档：`COMMENT_EXPORT_USAGE.md`
- 🐛 问题反馈：GitHub Issues
- 💬 技术讨论：社区论坛

---

**最后更新**: 2024-03-09  
**适用版本**: v1.0.0