# 🐛 Bug修复报告 - 视频URL解析问题

## 问题描述

用户通过Web界面使用"导出视频评论 (通过URL)"功能时，输入抖音短链接（如：`https://v.douyin.com/6JAfa8gV1Qs/`）后，系统提示没有评论。

## 根本原因

代码中获取视频ID时使用了错误的字段名：

```python
# ❌ 错误代码
aweme_id = data.get("aweme_id", "")
```

但是混合解析API（`hybrid_parsing_single_video`）返回的数据结构中，视频ID字段名是 `video_id`，而不是 `aweme_id`。

**API返回示例：**
```json
{
  "type": "video",
  "platform": "douyin",
  "video_id": "7614011226506546451",  // 🔍 注意这里是 video_id
  "desc": "伊朗强硬...",
  ...
}
```

## 解决方案

修改 `app/web/views/CommentExport.py` 文件中的第305行：

```python
# ✅ 修复后
aweme_id = data.get("aweme_id", "") or data.get("video_id", "")
```

同时添加了字段检查，确保能够获取到有效的视频ID：

```python
if not aweme_id:
    clear()
    put_error(
        ViewsUtils.t(
            "无法获取视频ID，请检查URL是否正确",
            "Failed to get video ID, please check if the URL is correct"
        )
    )
    put_link(ViewsUtils.t("返回主页", "Back to home"), "/")
    return
```

## 测试验证

### 测试URL
```
https://v.douyin.com/6JAfa8gV1Qs/
```

### 解析结果
- ✅ 视频ID：`7614011226506546451`
- ✅ 平台：`douyin`
- ✅ 标题：`伊朗强硬美国：要打就打持久战！川普的账，平不了了`

### 评论导出测试
```bash
curl -O "http://localhost:8000/api/douyin/comments/export?aweme_id=7614011226506546451&max_comments=5"
```

**结果：**
```
评论人,评论内容,点赞量,评论时间
夜猫子,巫师最近爆肝了，据说他又赔了，哈哈哈哈,5629,1970-01-21 20:26:31
榆树~舅时光,,856,1970-01-21 20:26:30
...
```

## 修改文件

- `app/web/views/CommentExport.py` (第305行)
  - 修改了视频ID获取逻辑
  - 添加了视频ID有效性检查

## 影响范围

- ✅ "导出视频评论 (通过URL)" 功能
- ✅ "导出视频评论 (通过ID)" 功能（未受影响）
- ✅ "批量解析视频" 页面的评论下载链接（未受影响）
- ✅ API端点（未受影响）

## 测试建议

1. **短链接测试**
   - 测试URL：`https://v.douyin.com/6JAfa8gV1Qs/`
   - 预期：正确解析并导出评论

2. **长链接测试**
   - 测试URL：`https://www.douyin.com/video/7372484719365098803`
   - 预期：正确解析并导出评论

3. **无效URL测试**
   - 测试URL：`https://example.com`
   - 预期：显示错误提示

## 相关文档

- API文档：`COMMENT_EXPORT_README.md`
- 使用说明：`COMMENT_EXPORT_USAGE.md`
- 示例代码：`COMMENT_EXAMPLES.md`

## 修复时间

2024-03-09

---

**服务器状态：** ✅ 运行中 (进程ID: 77966)  
**访问地址：** http://localhost:8000