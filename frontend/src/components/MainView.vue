<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import { mockIOSShortcut } from '@/assets/mock-data/shortcut'
import type { IOSShortcut } from '@/types/api'

const router = useRouter()
const configStore = useConfigStore()

const showModal = ref(false)
const modalContent = ref('')
const modalTitle = ref('')
const shortcutsData = ref<IOSShortcut>(mockIOSShortcut)

const features = [
  {
    id: 'parse',
    icon: '🔍',
    title: '批量解析视频',
    description: '支持抖音、TikTok、Bilibili批量解析',
    gradient: 'from-blue-500 to-blue-600'
  },
  {
    id: 'export-douyin-id',
    icon: '💬',
    title: '导出抖音评论',
    description: '通过视频URL/ID导出抖音视频评论到CSV',
    gradient: 'from-blue-500 to-blue-600'
  },
  {
    id: 'export-tiktok-id',
    icon: '🎬',
    title: '导出TikTok评论',
    description: '通过视频URL/ID导出TikTok视频评论到CSV',
    gradient: 'from-blue-500 to-blue-600'
  }
]

const handleOptionSelect = (optionId: string) => {
  switch (optionId) {
    case 'parse':
      router.push('/parse')
      break
    case 'export-douyin-id':
      router.push('/export/douyin')
      break
    case 'export-douyin-url':
      router.push('/export/douyin')
      break
    case 'export-tiktok-id':
      router.push('/export/tiktok')
      break
    case 'export-tiktok-url':
      router.push('/export/tiktok')
      break
    case 'easter-egg':
      if (configStore.easterEgg) {
        modalTitle.value = '小彩蛋'
        modalContent.value = '🎨 二次浓度++ (つ´ω`)つ'
        showModal.value = true
      }
      break
    default:
      modalTitle.value = '提示'
      modalContent.value = '功能开发中，敬请期待~'
      showModal.value = true
  }
}

const showShortcuts = () => {
  modalTitle.value = 'iOS快捷指令'
  modalContent.value = `
    <div class="space-y-4">
      <div class="text-sm text-gray-600">
        <div class="mb-3 p-3 bg-gray-50 rounded-lg">
          <p class="font-medium mb-1">版本: ${shortcutsData.value.version}</p>
          <p>更新时间: ${shortcutsData.value.update}</p>
        </div>
        <p class="mb-4">${shortcutsData.value.note}</p>
      </div>
      <div class="space-y-2">
        <a href="${shortcutsData.value.link}" target="_blank" 
           class="block w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 text-center">
          iOS快捷指令 (中文版)
        </a>
        <a href="${shortcutsData.value.link_en}" target="_blank"
           class="block w-full px-4 py-3 bg-neutral-100 text-neutral-700 rounded-lg font-medium hover:bg-neutral-200 transition-all duration-200 text-center">
          iOS Shortcut (English)
        </a>
      </div>
    </div>
  `
  showModal.value = true
}

const showDocument = () => {
  modalTitle.value = '开放接口'
  modalContent.value = `
    <div class="space-y-4">
      <p class="text-gray-600">完整的API文档请访问：</p>
      <a href="/docs" target="_blank" 
         class="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-all duration-200">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        查看API文档
      </a>
    </div>
  `
  showModal.value = true
}

const showAbout = () => {
  modalTitle.value = '关于'
  modalContent.value = `
    <div class="space-y-4">
      <div class="text-center py-4 bg-blue-50 rounded-lg">
        <img 
           src="/logo/logo192.png" 
           alt="Logo" 
           class="w-16 h-16 mx-auto mb-3 rounded-xl"
         />
        <h3 class="text-xl font-bold text-gray-800 mb-1">Douyin_TikTok_Download_API</h3>
        <p class="text-sm text-gray-500">版本 ${configStore.apiVersion}</p>
      </div>
      <div class="space-y-2 text-sm text-gray-600">
        <p><span class="inline-block w-20 font-medium">环境:</span> ${configStore.environment}</p>
        <p><span class="inline-block w-20 font-medium">更新:</span> ${configStore.updateTime}</p>
      </div>
      <div class="pt-2 border-t border-gray-100">
        <a href="https://github.com/Evil0ctal/Douyin_TikTok_Download_API" target="_blank" 
           class="inline-flex items-center w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-200">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
          </svg>
          访问GitHub项目
        </a>
      </div>
    </div>
  `
  showModal.value = true
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header class="text-center mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
        <div class="inline-flex items-center justify-center mb-6">
          <img 
             src="/logo/logo192.png" 
             alt="Logo" 
             class="w-20 h-20 rounded-2xl shadow-lg"
          />
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-3">
          抖音_TikTok_下载工具
        </h1>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
          抖音/TikTok/Bilibili 视频、评论下载工具
        </p>
      </header>

      <main class="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            选择功能
          </h2>
          <p class="text-gray-600">
            点击下方卡片快速访问功能
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <button
            v-for="feature in features"
            :key="feature.id"
            @click="handleOptionSelect(feature.id)"
            class="group relative bg-white border-2 border-gray-200 hover:border-blue-500 rounded-xl p-6 text-left shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <div class="flex items-start justify-between mb-3">
              <span class="text-3xl">{{ feature.icon }}</span>
              <div :class="feature.gradient" class="px-2.5 py-1 text-xs font-medium text-white rounded-full">
                新功能
              </div>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
              {{ feature.title }}
            </h3>
            <p class="text-sm text-gray-500">
              {{ feature.description }}
            </p>
            <div class="mt-4 pt-4 border-t border-gray-200 flex items-center text-sm text-blue-600 font-medium">
              立即使用
              <svg class="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </button>
        </div>
      </main>

      <footer class="mt-16 text-center text-sm text-gray-500">
        <p>&copy; {{ new Date().getFullYear() }} 下载工具. All rights reserved.</p>
      </footer>
    </div>

    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showModal" 
           class="fixed inset-0 z-50 flex items-center justify-center p-4"
           @click.self="showModal = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
          <div class="flex items-center justify-between p-5 border-b border-gray-100">
            <h3 class="text-lg font-semibold text-gray-900">{{ modalTitle }}</h3>
            <button 
              @click="showModal = false"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="p-6 overflow-y-auto max-h-[60vh]">
            <div class="text-gray-700" v-html="modalContent"></div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
