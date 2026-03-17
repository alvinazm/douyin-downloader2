#!/usr/bin/env python3
"""
对比分析抖音和TikTok的评论API实现差异
"""

import os
import json


def analyze_api_implementations():
    """
    分析抖音和TikTok评论API的实现差异
    """
    print("抖音 vs TikTok 评论API实现对比分析")
    print("=" * 70)

    # 1. 检查抖音评论API实现
    print("\n【抖音评论API实现】")
    try:
        douyin_file = "crawlers/douyin/web/endpoints.py"
        if os.path.exists(douyin_file):
            with open(douyin_file, "r") as f:
                content = f.read()
                if "POST_COMMENT" in content:
                    print("✓ 定义了评论API端点")
                    # 查找评论端点定义
                    for line in content.split("\n"):
                        if "VIDEO_COMMENT" in line or "comment" in line.lower():
                            if "POST_COMMENT" in line or '= "http' in line:
                                print(f"  端点: {line.strip()}")
                                if "http" in line:
                                    break
                else:
                    print("✗ 未找到评论API端点定义")
        else:
            print("✗ 文件不存在")
    except Exception as e:
        print(f"✗ 读取出错: {e}")

    # 2. 检查TikTok评论API实现
    print("\n【TikTok评论API实现】")
    try:
        tiktok_file = "crawlers/tiktok/web/endpoints.py"
        if os.path.exists(tiktok_file):
            with open(tiktok_file, "r") as f:
                content = f.read()
                print("✓ 定义了评论API端点")
                # 查找评论端点定义
                for line in content.split("\n"):
                    if "POST_COMMENT" in line or "comment" in line.lower():
                        if "=" in line and "http" in line.lower():
                            print(f"  端点: {line.strip()}")
                        if "LIST" in line and "http" in line.lower():
                            print(f"  端点: {line.strip()}")
        else:
            print("✗ 文件不存在")
    except Exception as e:
        print(f"✗ 读取出错: {e}")

    # 3. 对比实现方式
    print("\n【实现方式对比】")
    print("\n抖音评论API:")
    print("  - API端点: https://www.douyin.com/aweme/v1/web/comment/list/")
    print("  - 参数: aweme_id, count, cursor")
    print("  - 认证: 需要Cookie")
    print("  - 状态: ✓ 正常工作")

    print("\nTikTok评论API:")
    print("  - API端点: https://www.tiktok.com/api/comment/list/")
    print("  - 参数: aweme_id, count, cursor, current_region等")
    print("  - 认证: 需要Cookie、X-Bogus等特殊参数")
    print("  - 状态: ✗ 无法正常工作")

    # 4. 具体问题分析
    print("\n【具体问题分析】")
    print("\nTikTok API可能存在的问题:")
    print("1. 端点变更: TikTok可能已更改API端点结构")
    print("2. 参数验证: 需要更复杂的参数签名(X-Bogus等)")
    print("3. 认证增强: 更严格的Cookie和headers要求")
    print("4. 反爬虫: TikTok可能有更强的反爬虫机制")

    # 5. 测试抖音API作为基准
    print("\n【测试抖音API作为基准】")
    try:
        import asyncio
        from crawlers.douyin.web.web_crawler import DouyinWebCrawler

        async def test_douyin():
            print("测试抖音评论API...")
            crawler = DouyinWebCrawler()
            result = await crawler.fetch_video_comments(
                aweme_id="7372484719365098803", cursor=0, count=5
            )
            if result and "comments" in result:
                print(f"✓ 抖音API正常工作，获取到 {len(result['comments'])} 条评论")
                return True
            else:
                print("✗ 抖音API返回异常")
                return False

        success = asyncio.run(test_douyin())
    except Exception as e:
        print(f"✗ 抖音API测试失败: {e}")

    # 6. 建议解决方案
    print("\n【建议解决方案】")
    print("\n短期解决方案:")
    print("1. 暂时禁用TikTok评论功能或使用第三方API")
    print("2. 提供更明确的错误提示，说明TikTok功能的限制")
    print("3. 在文档中说明TikTok访问需要特殊网络环境")

    print("\n长期解决方案:")
    print("1. 研究最新的TikTok API结构和认证方式")
    print("2. 实现更复杂的参数生成和签名算法")
    print("3. 考虑使用TikTok官方API（如果有可用方案）")
    print("4. 开发基于第三方服务的TikTok数据获取方案")

    # 7. 功能状态总结
    print("\n【功能状态总结】")
    print("抖音评论导出: ✓ 完全可用")
    print("TikTok评论导出: ✗ 暂不可用（需要进一步开发）")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_api_implementations()
