#!/usr/bin/env python3
"""
TikTok评论获取失败原因综合诊断工具
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def diagnose_tiktok_issue(aweme_id: str):
    """
    诊断TikTok评论获取失败的原因
    """
    print("TikTok评论获取失败原因综合诊断")
    print("=" * 70)

    # 1. 测试基础网络连接
    print("\n【1】测试基础网络连接...")
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://www.tiktok.com/", follow_redirects=True
            )
            print(f"✓ TikTok主页可访问，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 无法连接TikTok: {e}")
        print("💡 原因: TikTok在您的网络环境下被限制访问")

    # 2. 测试API端点
    print("\n【2】测试TikTok API端点...")
    api_url = "https://www.tiktok.com/api/comment/list/"
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            test_url = f"{api_url}?aweme_id={aweme_id}&count=1"
            response = await client.get(test_url)
            print(f"API端点状态码: {response.status_code}")
            content = response.text[:500]

            if "404" in content or "notfound" in content.lower():
                print("✗ API端点返回404页面")
                print("💡 原因: API端点可能已更改或需要特定参数")
            elif "html" in content.lower():
                print("✗ 返回HTML页面而非JSON")
                print("💡 原因: 可能需要登录、Cookie失效或需要特殊headers")
            else:
                print(f"✓ 返回JSON响应")
                try:
                    data = json.loads(content)
                    print(f"数据结构: {list(data.keys())}")
                except:
                    print("✗ 无法解析JSON")

    except Exception as e:
        print(f"✗ 无法访问API端点: {e}")

    # 3. 测试TikTok爬虫功能
    print("\n【3】测试TikTok爬虫功能...")
    try:
        from crawlers.tiktok.web.web_crawler import TikTokWebCrawler

        crawler = TikTokWebCrawler()

        # 测试视频信息获取
        print("  - 测试视频信息获取...")
        video_data = await crawler.fetch_one_video(aweme_id)

        if video_data:
            print(f"✓ 可获取视频信息")
            print(
                f"  视频数据键: {list(video_data.keys()) if isinstance(video_data, dict) else 'N/A'}"
            )
            if "aweme_detail" in video_data:
                detail = video_data["aweme_detail"]
                print(f"  视频标题: {detail.get('desc', 'N/A')[:50]}...")
        else:
            print(f"✗ 无法获取视频信息")

        # 测试评论获取
        print("  - 测试评论获取...")
        comment_data = await crawler.fetch_post_comment(
            aweme_id=aweme_id, cursor=0, count=5, current_region="US"
        )

        if comment_data:
            print(f"✓ 可获取评论数据")
            print(
                f"  评论数据键: {list(comment_data.keys()) if isinstance(comment_data, dict) else 'N/A'}"
            )
            comments = comment_data.get("comments", [])
            print(f"  评论数量: {len(comments)}")
        else:
            print(f"✗ 无法获取评论数据")

    except Exception as e:
        print(f"✗ TikTok爬出错: {e}")
        import traceback

        print(f"错误详情: {traceback.format_exc()[-500:]}")

    # 4. 检查配置
    print("\n【4】检查TikTok配置...")
    try:
        config_path = "crawlers/tiktok/web/config.yaml"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                content = f.read()
                if "Cookie" in content:
                    print("✓ 配置文件包含Cookie")
                else:
                    print("⚠️ 配置文件中可能缺少Cookie")
        else:
            print("✗ 配置文件不存在")
    except:
        print("✗ 无法读取配置文件")

    # 5. 总结建议
    print("\n【诊断总结和建议】")
    print("=" * 70)

    print("\n可能的原因及解决方案：")
    print("\n1. 网络访问限制")
    print("   - 症状: 无法连接TikTok或连接超时")
    print("   - 原因: TikTok在中国大陆被屏蔽")
    print("   - 解决: 需要VPN/代理或部署在可访问TikTok的网络环境")

    print("\n2. API端点变更")
    print("   - 症状: 返回404页面或HTML")
    print("   - 原因: TikTok API接口已更新")
    print("   - 解决: 需要更新API端点和参数")

    print("\n3. 认证问题")
    print("   - 症状: 返回HTML登录页面")
    print("   - 原因: Cookie失效或需要登录")
    print("   - 解决: 更新有效的Cookie")

    print("\n4. 参数错误")
    print("   - 症状: API返回错误数据")
    print("   - 原因: 视频ID错误或参数格式不对")
    print("   - 解决: 确认视频ID是否正确")

    print("\n5. 视频无评论")
    print("   - 症状: API正常但返回空评论列表")
    print("   - 原因: 视频确实没有评论或评论被禁用")
    print("   - 解决: 尝试其他有评论的视频")

    print("\n【建议的测试步骤】")
    print("1. 确认您的网络可以正常访问TikTok网站")
    print("2. 使用TikTok浏览器开发者工具检查API请求")
    print("3. 对比抖音功能是否正常（作为基准）")
    print("4. 尝试不同的TikTok视频ID")
    print("5. 考虑部署到可访问TikTok的服务器")

    print("\n" + "=" * 70)


async def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 diagnose_tiktok_issue.py <aweme_id>")
        print("示例: python3 diagnose_tiktok_issue.py 7609213239641001217")
        sys.exit(1)

    aweme_id = sys.argv[1]
    await diagnose_tiktok_issue(aweme_id)


if __name__ == "__main__":
    asyncio.run(main())
