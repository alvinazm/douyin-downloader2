import type { VideoData } from '@/types/api'

export const mockDouyinVideo: VideoData = {
  type: 'video',
  platform: 'douyin',
  video_id: '7372484719365098803',
  desc: '这是一条抖音测试视频',
  create_time: Date.now() / 1000,
  author: {
    nickname: '测试用户',
    unique_id: 'test_user_123'
  },
  music: {
    id: '123456',
    title: '测试音乐',
    author: '音乐人',
    play_url: {
      url_list: ['https://example.com/music.mp3']
    }
  },
  statistics: {
    digg_count: 1234,
    comment_count: 56,
    share_count: 78,
    play_count: 9999
  },
  cover_data: {
    cover: 'https://example.com/cover.jpg',
    origin_cover: 'https://example.com/origin_cover.jpg',
    dynamic_cover: 'https://example.com/dynamic_cover.jpg'
  },
  hashtags: [
    { hashtag_name: '测试', hashtag_id: '123' }
  ],
  video_data: {
    wm_video_url: 'https://example.com/wm_video.mp4',
    wm_video_url_HQ: 'https://example.com/wm_video_hq.mp4',
    nwm_video_url: 'https://example.com/nwm_video.mp4',
    nwm_video_url_HQ: 'https://example.com/nwm_video_hq.mp4'
  }
}

export const mockTikTokVideo: VideoData = {
  type: 'video',
  platform: 'tiktok',
  video_id: '7372484719365098803',
  desc: 'This is a TikTok test video',
  create_time: Date.now() / 1000,
  author: {
    nickname: 'Test User',
    unique_id: 'test_user_tiktok'
  },
  music: {
    id: '789012',
    title: 'Test Music',
    author: 'Musician',
    play_url: {
      url_list: ['https://example.com/tiktok_music.mp3']
    }
  },
  statistics: {
    digg_count: 5678,
    comment_count: 123,
    share_count: 234,
    play_count: 50000
  },
  cover_data: {
    cover: 'https://example.com/tiktok_cover.jpg',
    origin_cover: 'https://example.com/tiktok_origin.jpg',
    dynamic_cover: 'https://example.com/tiktok_dynamic.jpg'
  },
  hashtags: [],
  video_data: {
    wm_video_url: 'https://example.com/tiktok_wm.mp4',
    wm_video_url_HQ: 'https://example.com/tiktok_wm_hq.mp4',
    nwm_video_url: 'https://example.com/tiktok_nwm.mp4',
    nwm_video_url_HQ: 'https://example.com/tiktok_nwm_hq.mp4'
  }
}

export const mockBilibiliVideo: VideoData = {
  type: 'video',
  platform: 'bilibili',
  video_id: 'BV1234567890',
  desc: '这是一条Bilibili测试视频',
  create_time: Date.now() / 1000,
  author: {
    nickname: 'Bilibili用户',
    unique_id: 'bilibili_user_123',
    uid: '12345678'
  },
  music: {
    id: '345678',
    title: 'B站背景音乐',
    author: 'UP主',
    play_url: {
      url_list: ['https://example.com/bilibili_music.mp3']
    }
  },
  statistics: {
    digg_count: 999,
    comment_count: 88,
    share_count: 45,
    play_count: 100000,
    collect_count: 500
  },
  cover_data: {
    cover: 'https://example.com/bilibili_cover.jpg',
    origin_cover: 'https://example.com/bilibili_origin.jpg',
    dynamic_cover: 'https://example.com/bilibili_dynamic.jpg'
  },
  hashtags: [
    { hashtag_name: 'bilibili', hashtag_id: '456' },
    { hashtag_name: '测试', hashtag_id: '789' }
  ],
  video_data: {
    wm_video_url: 'https://example.com/bilibili_wm.mp4',
    wm_video_url_HQ: 'https://example.com/bilibili_wm_hq.mp4',
    nwm_video_url: 'https://example.com/bilibili_nwm.mp4',
    nwm_video_url_HQ: 'https://example.com/bilibili_nwm_hq.mp4',
    audio_url: 'https://example.com/bilibili_audio.mp3'
  }
}
