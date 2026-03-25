# ==============================================================================
# Copyright (C) 2021 Evil0ctal
#
# This file is part of the Douyin_TikTok_Download_API project.
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# 　　　　 　　  ＿＿
# 　　　 　　 ／＞　　フ
# 　　　 　　| 　_　 _ l
# 　 　　 　／` ミ＿xノ
# 　　 　 /　　　 　 |       Feed me Stars ⭐ ️
# 　　　 /　 ヽ　　 ﾉ
# 　 　 │　　|　|　|
# 　／￣|　　 |　|　|
# 　| (￣ヽ＿_ヽ_)__)
# 　＼二つ
# ==============================================================================
#
# Contributor Link:
# - https://github.com/Evil0ctal
#
# ==============================================================================

import asyncio
import re
import httpx

from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫
from crawlers.tiktok.web.web_crawler import TikTokWebCrawler  # 导入TikTok Web爬虫
from crawlers.tiktok.app.app_crawler import TikTokAPPCrawler  # 导入TikTok App爬虫
from crawlers.bilibili.web.web_crawler import BilibiliWebCrawler  # 导入Bilibili Web爬虫
from crawlers.youtube.youtube_crawler import YouTubeCrawler  # 导入YouTube爬虫
from crawlers.utils.logger import logger  # 导入日志模块


class HybridCrawler:
    def __init__(self):
        self.DouyinWebCrawler = DouyinWebCrawler()
        self.TikTokWebCrawler = TikTokWebCrawler()
        self.TikTokAPPCrawler = TikTokAPPCrawler()
        self.BilibiliWebCrawler = BilibiliWebCrawler()
        self.YouTubeCrawler = YouTubeCrawler()

    async def get_bilibili_bv_id(self, url: str) -> str:
        """
        从 Bilibili URL 中提取 BV 号，支持短链重定向
        """
        # 如果是 b23.tv 短链，需要重定向获取真实URL
        if "b23.tv" in url:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, follow_redirects=True)
                url = str(response.url)

        # 从URL中提取BV号
        bv_pattern = r"(?:video\/|\/)(BV[A-Za-z0-9]+)"
        match = re.search(bv_pattern, url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Cannot extract BV ID from URL: {url}")

    async def hybrid_parsing_single_video(self, url: str, minimal: bool = False):
        logger.info(f"[HybridCrawler] 开始解析视频: URL={url}, minimal={minimal}")

        # 解析YouTube视频/Parse YouTube video
        if "youtube.com" in url or "youtu.be" in url or "youtube" in url.lower():
            platform = "youtube"
            logger.info(f"[HybridCrawler] 识别为YouTube视频")
            aweme_id = self.YouTubeCrawler.extract_video_id(url)
            if not aweme_id:
                raise ValueError(f"Cannot extract YouTube video ID from URL: {url}")
            logger.info(f"[HybridCrawler] YouTube Video ID: {aweme_id}")
            data = await self.YouTubeCrawler.fetch_video_info(url)
            aweme_type = 0  # YouTube only has video type
        # 解析抖音视频/Parse Douyin video
        elif "douyin" in url:
            platform = "douyin"
            logger.info(f"[HybridCrawler] 识别为抖音视频")
            aweme_id = await self.DouyinWebCrawler.get_aweme_id(url)
            logger.info(f"[HybridCrawler] Douyin Aweme ID: {aweme_id}")
            logger.info(f"[HybridCrawler] 开始获取抖音视频数据...")
            data = await self.DouyinWebCrawler.fetch_one_video(aweme_id)
            data = data.get("aweme_detail")
            # $.aweme_detail.aweme_type
            aweme_type = data.get("aweme_type")
            logger.info(
                f"[HybridCrawler] 抖音视频数据获取成功, aweme_type={aweme_type}"
            )
        # 解析TikTok视频/Parse TikTok video
        elif "tiktok" in url:
            platform = "tiktok"
            logger.info(f"[HybridCrawler] 识别为TikTok视频")
            logger.info(f"[HybridCrawler] 开始获取TikTok视频ID...")
            aweme_id = await self.TikTokWebCrawler.get_aweme_id(url)
            logger.info(f"[HybridCrawler] TikTok Aweme ID: {aweme_id}")

            # 2024-09-14: Switch to TikTokAPPCrawler instead of TikTokWebCrawler
            # data = await self.TikTokWebCrawler.fetch_one_video(aweme_id)
            # data = data.get("itemInfo").get("itemStruct")
            logger.info(f"[HybridCrawler] 开始获取TikTok视频数据 (使用APP API)...")
            data = await self.TikTokAPPCrawler.fetch_one_video(aweme_id)
            # $.imagePost exists if aweme_type is photo
            aweme_type = data.get("aweme_type")
            logger.info(
                f"[HybridCrawler] TikTok视频数据获取成功, aweme_type={aweme_type}"
            )
        # 解析Bilibili视频/Parse Bilibili video
        elif "bilibili" in url or "b23.tv" in url:
            platform = "bilibili"
            logger.info(f"[HybridCrawler] 识别为Bilibili视频")
            aweme_id = await self.get_bilibili_bv_id(url)  # BV号作为统一的video_id
            logger.info(f"[HybridCrawler] Bilibili BV ID: {aweme_id}")
            response = await self.BilibiliWebCrawler.fetch_one_video(aweme_id)
            data = response.get("data", {})  # 提取data部分
            # Bilibili只有视频类型，aweme_type设为0(video)
            aweme_type = 0
            logger.info(f"[HybridCrawler] Bilibili视频数据获取成功")
        else:
            logger.error(f"[HybridCrawler] 无法识别视频平台: URL={url}")
            raise ValueError(
                "hybrid_parsing_single_video: Cannot judge the video source from the URL."
            )

        logger.info(f"[HybridCrawler] 视频数据获取完成, platform={platform}")

        # 检查是否需要返回最小数据/Check if minimal data is required
        if not minimal:
            return data

        # 如果是最小数据，处理数据/If it is minimal data, process the data
        url_type_code_dict = {
            # common
            0: "video",
            # Douyin
            2: "image",
            4: "video",
            68: "image",
            # TikTok
            51: "video",
            55: "video",
            58: "video",
            61: "video",
            150: "image",
        }
        # 判断链接类型/Judge link type
        url_type = url_type_code_dict.get(aweme_type, "video")
        # print(f"url_type: {url_type}")

        """
        以下为(视频||图片)数据处理的四个方法,如果你需要自定义数据处理请在这里修改.
        The following are four methods of (video || image) data processing. 
        If you need to customize data processing, please modify it here.
        """

        """
        创建已知数据字典(索引相同)，稍后使用.update()方法更新数据
        Create a known data dictionary (index the same), 
        and then use the .update() method to update the data
        """

        # 根据平台适配字段映射
        if platform == "bilibili":
            result_data = {
                "type": url_type,
                "platform": platform,
                "video_id": aweme_id,
                "desc": data.get("title"),  # Bilibili使用title
                "create_time": data.get("pubdate"),  # Bilibili使用pubdate
                "author": data.get("owner"),  # Bilibili使用owner
                "music": None,  # Bilibili没有音乐信息
                "statistics": data.get("stat"),  # Bilibili使用stat
                "cover_data": {},  # 将在各平台处理中填充
                "hashtags": None,  # Bilibili没有hashtags概念
            }
        elif platform == "youtube":
            result_data = {
                "type": url_type,
                "platform": platform,
                "video_id": aweme_id,
                "aweme_id": aweme_id,  # 兼容前端字段
                "desc": data.get("title"),
                "create_time": data.get("upload_date"),
                "author": {"nickname": data.get("uploader"), "unique_id": None},
                "music": None,
                "statistics": {
                    "play_count": data.get("view_count"),
                    "digg_count": data.get("like_count"),
                },
                "cover_data": {},
                "hashtags": None,
            }
        else:
            result_data = {
                "type": url_type,
                "platform": platform,
                "video_id": aweme_id,  # 统一使用video_id字段，内容可能是aweme_id或bv_id
                "desc": data.get("desc"),
                "create_time": data.get("create_time"),
                "author": data.get("author"),
                "music": data.get("music"),
                "statistics": data.get("statistics"),
                "cover_data": {},  # 将在各平台处理中填充
                "hashtags": data.get("text_extra"),
            }
        # 创建一个空变量，稍后使用.update()方法更新数据/Create an empty variable and use the .update() method to update the data
        api_data = None
        # 判断链接类型并处理数据/Judge link type and process data
        # 抖音数据处理/Douyin data processing
        if platform == "douyin":
            # 填充封面数据
            result_data["cover_data"] = {
                "cover": data.get("video", {}).get("cover"),
                "origin_cover": data.get("video", {}).get("origin_cover"),
                "dynamic_cover": data.get("video", {}).get("dynamic_cover"),
            }
            # 抖音视频数据处理/Douyin video data processing
            if url_type == "video":
                # 将信息储存在字典中/Store information in a dictionary
                uri = data["video"]["play_addr"]["uri"]
                wm_video_url_HQ = data["video"]["play_addr"]["url_list"][0]
                wm_video_url = f"https://aweme.snssdk.com/aweme/v1/playwm/?video_id={uri}&radio=1080p&line=0"
                nwm_video_url_HQ = wm_video_url_HQ.replace("playwm", "play")
                nwm_video_url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"

                # 尝试获取更高质量的视频（遍历bit_rate获取最高质量）
                bit_rate_list = data.get("video", {}).get("bit_rate", [])
                if bit_rate_list:
                    # 按比特率排序，选择最高的
                    best_bitrate = max(
                        bit_rate_list, key=lambda x: x.get("bit_rate", 0)
                    )
                    best_play_addr = best_bitrate.get("play_addr", {})
                    nwm_video_url_HQ = best_play_addr.get(
                        "url_list", [nwm_video_url_HQ]
                    )[0]
                    wm_video_url_HQ = best_play_addr.get("url_list", [wm_video_url_HQ])[
                        0
                    ]
                    nwm_video_url = nwm_video_url_HQ
                    wm_video_url = wm_video_url_HQ

                api_data = {
                    "video_data": {
                        "wm_video_url": wm_video_url,
                        "wm_video_url_HQ": wm_video_url_HQ,
                        "nwm_video_url": nwm_video_url,
                        "nwm_video_url_HQ": nwm_video_url_HQ,
                    }
                }
            # 抖音图片数据处理/Douyin image data processing
            elif url_type == "image":
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                # 有水印图片列表/With watermark image list
                watermark_image_list = []
                # 遍历图片列表/Traverse image list
                for i in data["images"]:
                    no_watermark_image_list.append(i["url_list"][0])
                    watermark_image_list.append(i["download_url_list"][0])
                api_data = {
                    "image_data": {
                        "no_watermark_image_list": no_watermark_image_list,
                        "watermark_image_list": watermark_image_list,
                    }
                }
        # TikTok数据处理/TikTok data processing
        elif platform == "tiktok":
            # 填充封面数据
            result_data["cover_data"] = {
                "cover": data.get("video", {}).get("cover"),
                "origin_cover": data.get("video", {}).get("origin_cover"),
                "dynamic_cover": data.get("video", {}).get("dynamic_cover"),
            }
            # TikTok视频数据处理/TikTok video data processing
            if url_type == "video":
                # 将信息储存在字典中/Store information in a dictionary
                # wm_video = data['video']['downloadAddr']
                # wm_video = data['video']['download_addr']['url_list'][0]
                wm_video = (
                    data.get("video", {})
                    .get("download_addr", {})
                    .get("url_list", [None])[0]
                )

                # 尝试获取最高质量的视频（遍历bit_rate获取最高质量）
                bit_rate_list = data.get("video", {}).get("bit_rate", [])
                if bit_rate_list:
                    # 按比特率排序，选择最高的
                    best_bitrate = max(
                        bit_rate_list, key=lambda x: x.get("bit_rate", 0)
                    )
                    best_play_addr = best_bitrate.get("play_addr", {})
                    nwm_video_url_HQ = best_play_addr.get("url_list", [None])[0]
                else:
                    nwm_video_url_HQ = data["video"]["play_addr"]["url_list"][0]

                api_data = {
                    "video_data": {
                        "wm_video_url": wm_video,
                        "wm_video_url_HQ": wm_video,
                        "nwm_video_url": nwm_video_url_HQ,
                        "nwm_video_url_HQ": nwm_video_url_HQ,
                    }
                }
            # TikTok图片数据处理/TikTok image data processing
            elif url_type == "image":
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                # 有水印图片列表/With watermark image list
                watermark_image_list = []
                for i in data["image_post_info"]["images"]:
                    no_watermark_image_list.append(i["display_image"]["url_list"][0])
                    watermark_image_list.append(
                        i["owner_watermark_image"]["url_list"][0]
                    )
                api_data = {
                    "image_data": {
                        "no_watermark_image_list": no_watermark_image_list,
                        "watermark_image_list": watermark_image_list,
                    }
                }
        # Bilibili数据处理/Bilibili data processing
        elif platform == "bilibili":
            # 填充封面数据
            result_data["cover_data"] = {
                "cover": data.get("pic"),  # Bilibili使用pic作为封面
                "origin_cover": data.get("pic"),
                "dynamic_cover": data.get("pic"),
            }
            # Bilibili只有视频，直接处理视频数据
            if url_type == "video":
                # 获取视频播放地址需要额外调用API
                cid = data.get("cid")  # 获取cid
                if cid:
                    # 获取播放链接，cid需要转换为字符串
                    playurl_data = await self.BilibiliWebCrawler.fetch_video_playurl(
                        aweme_id, str(cid)
                    )

                    data = playurl_data.get("data", {})
                    dash = data.get("dash", {})
                    durl = data.get("durl", [])  # 非DASH格式的视频URL列表

                    video_list = dash.get("video", [])
                    audio_list = dash.get("audio", [])

                    video_url = None
                    audio_url = None

                    # 优先从 durl 获取最高质量（非DASH格式通常更高清）
                    if durl:
                        # 按 size 字段排序，选择最大的
                        best_durl = max(durl, key=lambda x: x.get("size", 0))
                        video_url = best_durl.get("url")
                        # durl格式中音视频在一起，不需要单独获取音频
                    elif video_list:
                        # quality值越大越清晰
                        best_video = max(video_list, key=lambda x: x.get("quality", 0))
                        video_url = best_video.get("baseUrl")
                        # 选择最高质量的音频流
                        audio_url = audio_list[0].get("baseUrl") if audio_list else None

                    api_data = {
                        "video_data": {
                            "wm_video_url": video_url,
                            "wm_video_url_HQ": video_url,
                            "nwm_video_url": video_url,  # Bilibili没有水印概念
                            "nwm_video_url_HQ": video_url,
                            "audio_url": audio_url,  # Bilibili音视频分离
                            "cid": cid,  # 保存cid供后续使用
                        }
                    }
                else:
                    api_data = {
                        "video_data": {
                            "wm_video_url": None,
                            "wm_video_url_HQ": None,
                            "nwm_video_url": None,
                            "nwm_video_url_HQ": None,
                            "error": "Failed to get cid for video playback",
                        }
                    }
        # YouTube数据处理/YouTube data processing
        elif platform == "youtube":
            result_data["cover_data"] = {
                "cover": data.get("thumbnail"),
                "origin_cover": data.get("thumbnail"),
                "dynamic_cover": data.get("thumbnail"),
            }
            if url_type == "video":
                full_info = data.get("full_info", {})
                formats = full_info.get("formats", [])
                video_url = None
                audio_url = None

                for f in formats:
                    if f.get("url"):
                        if f.get("vcodec") != "none" and f.get("acodec") != "none":
                            video_url = f.get("url")
                            break
                        elif f.get("vcodec") != "none" and video_url is None:
                            video_url = f.get("url")
                        elif f.get("acodec") != "none" and audio_url is None:
                            audio_url = f.get("url")

                api_data = {
                    "video_data": {
                        "wm_video_url": video_url,
                        "wm_video_url_HQ": video_url,
                        "nwm_video_url": video_url,
                        "nwm_video_url_HQ": video_url,
                        "audio_url": audio_url,
                    }
                }
        # 更新数据/Update data
        result_data.update(api_data)
        return result_data

    async def main(self):
        # 测试混合解析单一视频接口/Test hybrid parsing single video endpoint
        # url = "https://v.douyin.com/L4FJNR3/"
        # url = "https://www.tiktok.com/@taylorswift/video/7359655005701311786"
        url = "https://www.tiktok.com/@flukegk83/video/7360734489271700753"
        # url = "https://www.tiktok.com/@minecraft/photo/7369296852669205791"
        minimal = True
        result = await self.hybrid_parsing_single_video(url, minimal=minimal)
        print(result)

        # 占位
        pass


if __name__ == "__main__":
    # 实例化混合爬虫/Instantiate hybrid crawler
    hybird_crawler = HybridCrawler()
    # 运行测试代码/Run test code
    asyncio.run(hybird_crawler.main())
