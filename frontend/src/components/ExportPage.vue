<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import CommentExport from './CommentExport.vue'

const router = useRouter()

const props = defineProps<{
  platform: 'douyin' | 'tiktok'
}>()

const platformName = computed(() => {
  return props.platform === 'douyin' ? '抖音' : 'TikTok'
})
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header class="mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
        <button 
          @click="router.push('/')"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-lg font-medium shadow-sm hover:shadow-md hover:text-blue-600 transition-all duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          返回主页
        </button>
      </header>

      <main class="animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            导出{{ platformName }}视频评论
          </h1>
          <p class="text-gray-600">
            通过视频ID或URL导出{{ platformName }}视频评论到CSV文件
          </p>
        </div>

        <CommentExport :platform="platform" />
      </main>
    </div>
  </div>
</template>
