import asyncio
import os

import yaml
import aiohttp
from pywebio.input import *
from pywebio.output import *
from pywebio.session import download as pywebio_download

from app.web.views.ViewsUtils import ViewsUtils
from crawlers.douyin.web.web_crawler import DouyinWebCrawler

Crawler = DouyinWebCrawler()

# 读取配置文件
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "config.yaml",
)
with open(config_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


class CommentExporter:
    def __init__(self):
        pass

    @staticmethod
    async def fetch_all_comments(aweme_id: str, max_comments: int = None):
        """
        获取视频的所有评论（支持分页）
        """
        all_comments = []
        cursor = 0
        count = 20
        total_count = 0

        # 在async函数外输出开始信息
        # put_info(
        #     ViewsUtils.t(
        #         f"开始获取视频 {aweme_id} 的评论...",
        #         f"Start fetching comments for video {aweme_id}...",
        #     )
        # )

        while True:
            try:
                # 在async函数外输出进度信息
                # put_info(
                #     ViewsUtils.t(
                #         f"已获取 {total_count} 条评论...",
                #         f"Fetched {total_count} comments...",
                #     )
                # )

                response = await Crawler.fetch_video_comments(
                    aweme_id=aweme_id, cursor=cursor, count=count
                )

                if not response or "comments" not in response:
                    print(f"Response is empty or no comments: {response}")
                    break

                comments = response.get("comments", [])
                if not comments:
                    print(f"No comments in response")
                    break

                all_comments.extend(comments)
                total_count += len(comments)
                print(f"获取到 {len(comments)} 条评论，总计 {total_count} 条")

                # 如果达到最大评论数，停止获取
                if max_comments and total_count >= max_comments:
                    all_comments = all_comments[:max_comments]
                    break

                # 更新游标
                cursor = response.get("cursor", 0)
                has_more = response.get("has_more", False)
                print(f"游标: {cursor}, has_more: {has_more}")

                if has_more == False:
                    break

                # 添加延迟，避免请求过快
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Error fetching comments: {str(e)}")
                import traceback

                traceback.print_exc()
                break

        return all_comments

    @staticmethod
    def parse_comment_data(comment):
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
                from datetime import datetime

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
            return None

    @staticmethod
    def generate_csv_content(comments):
        """
        生成CSV内容（返回bytes）
        """
        import csv
        from io import StringIO, BytesIO

        # 使用StringIO生成CSV字符串
        output = StringIO()
        fieldnames = ["评论人", "评论内容", "点赞量", "评论时间"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        # 写入BOM以确保Excel能正确显示中文
        output.write("\ufeff")

        # 写入表头
        writer.writeheader()

        # 写入数据
        for comment in comments:
            parsed_data = CommentExporter.parse_comment_data(comment)
            if parsed_data:
                writer.writerow(parsed_data)

        # 将字符串转换为bytes（UTF-8编码）
        csv_string = output.getvalue()
        csv_bytes = csv_string.encode("utf-8")

        return csv_bytes


def export_comments_from_id():
    """
    通过视频ID导出评论
    """
    put_markdown(ViewsUtils.t("## 📝 导出视频评论功能", "## 📝 Export Video Comments"))
    put_row([put_html("<br>")])

    aweme_id = input(
        ViewsUtils.t("请输入视频ID (aweme_id)", "Please enter video ID (aweme_id)"),
        type=TEXT,
        required=True,
        placeholder="7372484719365098803",
        help_text=ViewsUtils.t(
            "例如：7372484719365098803", "Example: 7372484719365098803"
        ),
    )

    max_comments = input(
        ViewsUtils.t("最大评论数", "Max comments (optional)"),
        type=NUMBER,
        value=100,
        required=False,
        help_text=ViewsUtils.t(
            "默认100条，建议不要设置过大", "Default 100, suggested not to set too high"
        ),
    )

    put_row([put_html("<br>")])

    # 获取评论
    put_info(
        ViewsUtils.t(
            f"正在获取视频 {aweme_id} 的评论，请稍候...",
            f"Fetching comments for video {aweme_id}, please wait...",
        )
    )

    comments = asyncio.run(CommentExporter.fetch_all_comments(aweme_id, max_comments))

    if not comments:
        put_error(ViewsUtils.t("未找到任何评论", "No comments found"))
        put_link(ViewsUtils.t("返回主页", "Back to home"), "/")
        return

    put_success(
        ViewsUtils.t(
            f"成功获取 {len(comments)} 条评论！",
            f"Successfully fetched {len(comments)} comments!",
        )
    )

    # 生成CSV内容
    csv_content = CommentExporter.generate_csv_content(comments)

    # 生成文件名
    filename = f"douyin_comments_{aweme_id}.csv"

    put_row([put_html("<br>")])
    put_markdown(ViewsUtils.t("### 📥 下载评论文件", "### 📥 Download Comments File"))
    put_info(
        ViewsUtils.t(
            "点击下方按钮下载CSV文件", "Click the button below to download CSV file"
        )
    )

    # 创建下载按钮
    put_button(
        ViewsUtils.t("下载 CSV 文件", "Download CSV File"),
        onclick=lambda: pywebio_download(filename, csv_content),
        color="primary",
    )

    put_row([put_html("<br><br>")])

    # 显示部分评论预览
    put_markdown(
        ViewsUtils.t("### 👀 评论预览 (前5条)", "### 👀 Comment Preview (First 5)")
    )

    from pywebio.output import put_table

    table_data = [
        [
            ViewsUtils.t("评论人", "User"),
            ViewsUtils.t("评论内容", "Content"),
            ViewsUtils.t("点赞量", "Likes"),
            ViewsUtils.t("评论时间", "Time"),
        ]
    ]

    for comment in comments[:5]:
        parsed = CommentExporter.parse_comment_data(comment)
        if parsed:
            table_data.append(
                [
                    parsed["评论人"],
                    parsed["评论内容"][:50] + "..."
                    if len(parsed["评论内容"]) > 50
                    else parsed["评论内容"],
                    parsed["点赞量"],
                    parsed["评论时间"],
                ]
            )

    put_table(table_data)

    put_row([put_html("<br>")])
    put_link(ViewsUtils.t("返回主页", "Back to home"), "/")


def export_comments_from_url():
    """
    通过视频URL导出评论
    """
    put_markdown(ViewsUtils.t("## 📝 导出视频评论功能", "## 📝 Export Video Comments"))
    put_row([put_html("<br>")])

    url = input(
        ViewsUtils.t("请输入抖音视频URL", "Please enter Douyin video URL"),
        type=TEXT,
        required=True,
        placeholder="https://www.douyin.com/video/7372484719365098803",
        help_text=ViewsUtils.t("支持长链接或短链接", "Support long or short URL"),
    )

    put_info(ViewsUtils.t("正在解析视频信息...", "Parsing video information..."))

    # 解析视频获取aweme_id
    try:
        from crawlers.hybrid.hybrid_crawler import HybridCrawler

        hybrid_crawler = HybridCrawler()
        data = asyncio.run(
            hybrid_crawler.hybrid_parsing_single_video(url, minimal=True)
        )

        if data.get("platform") != "douyin":
            put_error(
                ViewsUtils.t(
                    "仅支持抖音视频评论导出",
                    "Only Douyin video comment export is supported",
                )
            )
            put_link(ViewsUtils.t("返回主页", "Back to home"), "/")
            return

        aweme_id = data.get("aweme_id", "") or data.get("video_id", "")

        if not aweme_id:
            clear()
            put_error(
                ViewsUtils.t(
                    "无法获取视频ID，请检查URL是否正确",
                    "Failed to get video ID, please check if the URL is correct",
                )
            )
            put_link(ViewsUtils.t("返回主页", "Back to home"), "/")
            return

        clear()
        put_success(
            ViewsUtils.t(
                f"成功解析视频ID: {aweme_id}",
                f"Successfully parsed video ID: {aweme_id}",
            )
        )
        put_row([put_html("<br>")])

        # 继续导出流程
        export_comments_from_id_impl(aweme_id)

    except Exception as e:
        clear()
        put_error(
            ViewsUtils.t(f"解析视频失败: {str(e)}", f"Failed to parse video: {str(e)}")
        )
        put_link(ViewsUtils.t("返回主页", "Back to home"), "/")


def export_comments_from_id_impl(aweme_id: str):
    """
    通过视频ID导出评论的实现函数
    """
    max_comments = input(
        ViewsUtils.t("最大评论数", "Max comments (optional)"),
        type=NUMBER,
        value=100,
        required=False,
        help_text=ViewsUtils.t("默认100条", "Default 100"),
    )

    put_row([put_html("<br>")])

    # 获取评论
    comments = asyncio.run(CommentExporter.fetch_all_comments(aweme_id, max_comments))

    if not comments:
        put_error(ViewsUtils.t("未找到任何评论", "No comments found"))
        put_link(ViewsUtils.t("返回主页", "Back to home"), "/")
        return

    put_success(
        ViewsUtils.t(
            f"成功获取 {len(comments)} 条评论！",
            f"Successfully fetched {len(comments)} comments!",
        )
    )

    # 生成CSV内容
    csv_content = CommentExporter.generate_csv_content(comments)

    # 生成文件名
    filename = f"douyin_comments_{aweme_id}.csv"

    put_row([put_html("<br>")])
    put_markdown(ViewsUtils.t("### 📥 下载评论文件", "### 📥 Download Comments File"))
    put_button(
        ViewsUtils.t("下载 CSV 文件", "Download CSV File"),
        onclick=lambda: pywebio_download(filename, csv_content),
        color="primary",
    )

    put_row([put_html("<br><br>")])

    # 显示部分评论预览
    put_markdown(
        ViewsUtils.t("### 👀 评论预览 (前5条)", "### 👀 Comment Preview (First 5)")
    )
    from pywebio.output import put_table

    table_data = [
        [
            ViewsUtils.t("评论人", "User"),
            ViewsUtils.t("评论内容", "Content"),
            ViewsUtils.t("点赞量", "Likes"),
            ViewsUtils.t("评论时间", "Time"),
        ]
    ]

    for comment in comments[:5]:
        parsed = CommentExporter.parse_comment_data(comment)
        if parsed:
            table_data.append(
                [
                    parsed["评论人"],
                    parsed["评论内容"][:50] + "..."
                    if len(parsed["评论内容"]) > 50
                    else parsed["评论内容"],
                    parsed["点赞量"],
                    parsed["评论时间"],
                ]
            )

    put_table(table_data)

    put_row([put_html("<br>")])
    put_link(ViewsUtils.t("返回主页", "Back to home"), "/")
