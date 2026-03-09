#!/usr/bin/env python3
"""
抖音视频评论导出工具
使用方法：
    python3 comment_export_tool.py <aweme_id> [max_comments]

示例：
    python3 comment_export_tool.py 7372484719365098803 100
"""

import sys
import os
import asyncio
import csv
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawlers.douyin.web.web_crawler import DouyinWebCrawler


class CommentExporter:
    def __init__(self):
        self.crawler = DouyinWebCrawler()

    async def fetch_all_comments(self, aweme_id: str, max_comments: int = None):
        """
        获取视频的所有评论（支持分页）
        """
        all_comments = []
        cursor = 0
        count = 20
        total_count = 0

        print(f"开始获取评论... (aweme_id: {aweme_id})")

        while True:
            try:
                print(f"获取第 {total_count // count + 1} 页评论...")
                response = await self.crawler.fetch_video_comments(
                    aweme_id=aweme_id, cursor=cursor, count=count
                )

                if not response:
                    print("未获取到响应，停止获取")
                    break

                if "comments" not in response:
                    print("响应中没有评论数据，停止获取")
                    break

                comments = response.get("comments", [])
                if not comments:
                    print("没有更多评论，停止获取")
                    break

                all_comments.extend(comments)
                total_count += len(comments)
                print(f"已获取 {total_count} 条评论")

                # 如果达到最大评论数，停止获取
                if max_comments and total_count >= max_comments:
                    all_comments = all_comments[:max_comments]
                    print(f"已达到最大评论数 {max_comments}，停止获取")
                    break

                # 更新游标
                cursor = response.get("cursor", 0)
                has_more = response.get("has_more", False)

                print(f"游标: {cursor}, 是否有更多: {has_more}")

                if not has_more:
                    print("没有更多评论了，停止获取")
                    break

                # 添加延迟，避免请求过快
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"获取评论时出错: {e}")
                import traceback

                traceback.print_exc()
                break

        print(f"完成！共获取 {len(all_comments)} 条评论")
        return all_comments

    def parse_comment_data(self, comment):
        """
        解析单条评论数据，提取所需字段
        """
        try:
            user_info = comment.get("user", {})
            text = comment.get("text", "")
            digg_count = comment.get("digg_count", 0)
            create_time = comment.get("create_time", 0)

            # 将时间戳转换为可读时间
            if create_time:
                # 抖音的时间戳已经是秒级，不需要转换
                time_str = datetime.fromtimestamp(create_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            else:
                time_str = ""

            nickname = user_info.get("nickname", "未知用户")

            return {
                "评论人": nickname,
                "评论内容": text,
                "点赞量": digg_count,
                "评论时间": time_str,
            }
        except Exception as e:
            print(f"解析评论数据时出错: {e}")
            return None

    def save_to_csv(self, comments, file_path: str):
        """
        将评论数据保存到CSV文件
        """
        try:
            print(f"开始保存CSV文件... ({file_path})")

            # 创建目录
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # 写入CSV文件
            with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # 写入表头
                writer.writeheader()

                # 写入数据
                success_count = 0
                for comment in comments:
                    parsed_data = self.parse_comment_data(comment)
                    if parsed_data:
                        writer.writerow(parsed_data)
                        success_count += 1

                print(f"成功写入 {success_count} 条评论数据")

            print(f"CSV文件保存成功: {file_path}")
            return True
        except Exception as e:
            print(f"保存CSV文件时出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def export_comments_to_csv(
        self, aweme_id: str, max_comments: int = 100, output_file: str = None
    ):
        """
        导出评论到CSV文件
        """
        # 生成文件名
        if not output_file:
            output_file = f"download/comments/douyin_comments_{aweme_id}.csv"

        # 获取所有评论
        comments = await self.fetch_all_comments(aweme_id, max_comments)

        if not comments:
            print("未找到任何评论")
            return False

        # 保存到CSV
        success = self.save_to_csv(comments, output_file)

        if success:
            print(f"\n导出成功！文件路径: {os.path.abspath(output_file)}")
            return True
        else:
            print("\n导出失败")
            return False


async def main():
    if len(sys.argv) < 2:
        print(
            "使用方法: python3 comment_export_tool.py <aweme_id> [max_comments] [output_file]"
        )
        print("示例: python3 comment_export_tool.py 7372484719365098803 100")
        sys.exit(1)

    aweme_id = sys.argv[1]
    max_comments = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    exporter = CommentExporter()
    await exporter.export_comments_to_csv(aweme_id, max_comments, output_file)


if __name__ == "__main__":
    asyncio.run(main())
