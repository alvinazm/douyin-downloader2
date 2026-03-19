import type { VideoData } from './api'

/**
 * Mock 视频数据 - 抖音视频
 */
export const mockDouyinVideo: VideoData = {
  type: 'video',
  platform: 'douyin',
  video_id: '7372484719365098803',
  desc: '这是一个抖音视频示例 #抖音推荐 #热门',
  create_time: 1710662400,
  author: {
    nickname: '抖音用户',
    unique_id: 'douyin_user_123',
    sec_uid: 'MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM',
    avatar_thumb: 'https://example.com/avatar.jpg'
  },
  music: {
    id: '123456',
    title: '原声音乐',
    author: '音乐作者',
    play_url: {
      url_list: ['https://example.com/music.mp3']
    }
  },
  statistics: {
    digg_count: 10000,
    comment_count: 500,
    share_count: 200,
    play_count: 100000,
    collect_count: 1000
  },
  cover_data: {
    cover: 'https://example.com/cover.jpg',
    origin_cover: 'https://example.com/origin_cover.jpg',
    dynamic_cover: 'https://example.com/dynamic_cover.jpg'
  },
  hashtags: [
    {
      hashtag_name: '抖音推荐',
      hashtag_id: '1'
    },
    {
      hashtag_name: '热门',
      hashtag_id: '2'
    }
  ],
  video_data: {
    wm_video_url: 'https://example.com/video_wm.mp4',
    wm_video_url_HQ: 'https://example.com/video_wm_hq.mp4',
    nwm_video_url: 'https://example.com/video_nwm.mp4',
    nwm_video_url_HQ: 'https://example.com/video_nwm_hq.mp4'
  }
}

/**
 * Mock 视频数据 - TikTok视频
 */
export const mockTikTokVideo: VideoData = {
  type: 'video',
  platform: 'tiktok',
  video_id: '7360734489271700753',
  desc: 'This is a TikTok video example #fyp #viral',
  create_time: 1710662400,
  author: {
    nickname: 'TikTok User',
    unique_id: '@tiktok_user',
    sec_uid: 'MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM',
    avatar_thumb: 'https://example.com/avatar.jpg'
  },
  music: {
    id: '789012',
    title: 'Original Sound',
    author: 'Music Artist',
    play_url: {
      url_list: ['https://example.com/music.mp3']
    }
  },
  statistics: {
    digg_count: 50000,
    comment_count: 2000,
    share_count: 1000,
    play_count: 500000,
    collect_count: 5000
  },
  cover_data: {
    cover: 'https://example.com/cover.jpg',
    origin_cover: 'https://example.com/origin_cover.jpg',
    dynamic_cover: 'https://example.com/dynamic_cover.jpg'
  },
  hashtags: [
    {
      hashtag_name: 'fyp',
      hashtag_id: '1'
    },
    {
      hashtag_name: 'viral',
      hashtag_id: '2'
    }
  ],
  video_data: {
    wm_video_url: 'https://example.com/video_wm.mp4',
    wm_video_url_HQ: 'https://example.com/video_wm_hq.mp4',
    nwm_video_url: 'https://example.com/video_nwm.mp4',
    nwm_video_url_HQ: 'https://example.com/video_nwm_hq.mp4'
  }
}

/**
 * Mock 视频数据 - Bilibili视频
 */
export const mockBilibiliVideo: VideoData = {
  type: 'video',
  platform: 'bilibili',
  video_id: 'BV1M1421t7hT',
  desc: '这是一个Bilibili视频示例',
  create_time: 1710662400,
  author: {
    nickname: 'Bilibili用户',
    unique_id: 'bilibili_user',
    uid: '123456789'
  },
  music: null,
  statistics: {
    digg_count: 30000,
    comment_count: 1000,
    share_count: 500,
    play_count: 200000
  },
  cover_data: {
    cover: 'https://example.com/cover.jpg',
    origin_cover: 'https://example.com/cover.jpg',
    dynamic_cover: 'https://example.com/cover.jpg'
  },
  hashtags: null,
  video_data: {
    wm_video_url: 'https://example.com/video.mp4',
    wm_video_url_HQ: 'https://example.com/video_hq.mp4',
    nwm_video_url: 'https://example.com/video.mp4',
    nwm_video_url_HQ: 'https://example.com/video_hq.mp4',
    audio_url: 'https://example.com/audio.mp3'
  }
}

/**
 * Mock 视频数据 - 抖音图集
 */
export const mockDouyinImage: VideoData = {
  type: 'image',
  platform: 'douyin',
  video_id: '7372484719365098804',
  desc: '这是一个抖音图集示例 #图集推荐',
  create_time: 1710662400,
  author: {
    nickname: '抖音图集作者',
    unique_id: 'douyin_image_author',
    sec_uid: 'MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM'
  },
  music: null,
  statistics: {
    digg_count: 5000,
    comment_count: 100,
    share_count: 50,
    play_count: 20000,
    collect_count: 500
  },
  cover_data: {
    cover: 'https://example.com/cover.jpg',
    origin_cover: 'https://example.com/origin_cover.jpg',
    dynamic_cover: 'https://example.com/dynamic_cover.jpg'
  },
  hashtags: [
    {
      hashtag_name: '图集推荐',
      hashtag_id: '1'
    }
  ],
  image_data: {
    no_watermark_image_list: [
      'https://example.com/image1.jpg',
      'https://example.com/image2.jpg',
      'https://example.com/image3.jpg'
    ],
    watermark_image_list: [
      'https://example.com/image1_wm.jpg',
      'https://example.com/image2_wm.jpg',
      'https://example.com/image3_wm.jpg'
    ]
  }
}
