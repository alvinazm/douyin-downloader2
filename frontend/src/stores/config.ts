import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { VideoData } from '@/types/api'

/**
 * 配置状态管理
 */
export const useConfigStore = defineStore('config', () => {
  // 状态
  const apiVersion = ref('V4.1.2')
  const updateTime = ref('2025/03/16')
  const environment = ref('Demo')
  const maxTakeUrls = ref(30) // 单词最大解析链接数量30个
  const downloadSwitch = ref(true)
  const downloadFilePrefix = ref('douyin.wtf_')
  const easterEgg = ref(true)
  const live2DEnable = ref(true)

  // 计算属性
  const isProduction = computed(() => environment.value === 'Production')
  const isDemo = computed(() => environment.value === 'Demo')

  // 方法
  const updateConfig = (newConfig: Partial<typeof import('./config').default>) => {
    if (newConfig.apiVersion !== undefined) apiVersion.value = newConfig.apiVersion
    if (newConfig.updateTime !== undefined) updateTime.value = newConfig.updateTime
    if (newConfig.environment !== undefined) environment.value = newConfig.environment
    if (newConfig.maxTakeUrls !== undefined) maxTakeUrls.value = newConfig.maxTakeUrls
    if (newConfig.downloadSwitch !== undefined) downloadSwitch.value = newConfig.downloadSwitch
    if (newConfig.downloadFilePrefix !== undefined) downloadFilePrefix.value = newConfig.downloadFilePrefix
    if (newConfig.easterEgg !== undefined) easterEgg.value = newConfig.easterEgg
    if (newConfig.live2DEnable !== undefined) live2DEnable.value = newConfig.live2DEnable
  }

  return {
    // 状态
    apiVersion,
    updateTime,
    environment,
    maxTakeUrls,
    downloadSwitch,
    downloadFilePrefix,
    easterEgg,
    live2DEnable,

    // 计算属性
    isProduction,
    isDemo,

    // 方法
    updateConfig
  }
})
