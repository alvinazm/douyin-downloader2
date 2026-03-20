import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiClient } from '@/api'
import type { VideoData } from '@/types/api'

/**
 * 配置状态管理
 */
export const useConfigStore = defineStore('config', () => {
  // 状态 - 初始值从服务器加载，这里只给默认fallback值
  const apiVersion = ref('')
  const updateTime = ref('')
  const environment = ref('')
  const maxTakeUrls = ref(0)
  const maxComments = ref(0)
  const downloadSwitch = ref(true)
  const downloadFilePrefix = ref('')
  const easterEgg = ref(true)
  const live2DEnable = ref(true)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isProduction = computed(() => environment.value === 'Production')
  const isDemo = computed(() => environment.value === 'Demo')

  // 方法
  const updateConfig = (newConfig: Partial<any>) => {
    if (newConfig.maxComments !== undefined) maxComments.value = newConfig.maxComments
    if (newConfig.maxTakeUrls !== undefined) maxTakeUrls.value = newConfig.maxTakeUrls
    if (newConfig.apiVersion !== undefined) apiVersion.value = newConfig.apiVersion
    if (newConfig.environment !== undefined) environment.value = newConfig.environment
  }

  // 从后端加载配置
  const loadConfig = async () => {
    try {
      isLoading.value = true
      error.value = null
      const config = await ApiClient.getConfig()
      updateConfig(config)
      console.log('配置加载成功:', config)
    } catch (err: any) {
      console.error('配置加载失败:', err)
      error.value = err.message || '加载配置失败'
    } finally {
      isLoading.value = false
    }
  }

  return {
    // 状态
    apiVersion,
    updateTime,
    environment,
    maxTakeUrls,
    maxComments,
    downloadSwitch,
    downloadFilePrefix,
    easterEgg,
    live2DEnable,
    isLoading,
    error,

    // 计算属性
    isProduction,
    isDemo,

    // 方法
    updateConfig,
    loadConfig
  }
})
