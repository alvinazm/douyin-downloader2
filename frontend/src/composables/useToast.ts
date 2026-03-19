import { ref } from 'vue'

/**
 * Toast 通知 Composable
 * @returns Toast 相关方法和状态
 */
export function useToast() {
  const toasts = ref<Array<{
    id: string
    message: string
    type: 'success' | 'error' | 'warning' | 'info'
    duration: number
    timestamp: number
  }>>([])

  /**
   * 显示 Toast
   * @param message 消息内容
   * @param type Toast类型
   * @param duration 持续时间（ms），默认3000
   */
  const showToast = (
    message: string,
    type: 'success' | 'error' | 'warning' | 'info' = 'info',
    duration: number = 3000
  ): void => {
    const id = `toast-${Date.now()}-${Math.random()}`
    const toast = {
      id,
      message,
      type,
      duration,
      timestamp: Date.now()
    }

    toasts.value.push(toast)

    // 自动移除
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
  }

  /**
   * 移除 Toast
   * @param id Toast ID
   */
  const removeToast = (id: string): void => {
    const index = toasts.value.findIndex(t => t.id === id)

    if (index >= 0) {
      toasts.value.splice(index, 1)
    }
  }

  /**
   * 显示成功消息
   */
  const showSuccess = (message: string, duration?: number): void => {
    showToast(message, 'success', duration)
  }

  /**
   * 显示错误消息
   */
  const showError = (message: string, duration?: number): void => {
    showToast(message, 'error', duration)
  }

  /**
   * 显示警告消息
   */
  const showWarning = (message: string, duration?: number): void => {
    showToast(message, 'warning', duration)
  }

  /**
   * 显示信息消息
   */
  const showInfo = (message: string, duration?: number): void => {
    showToast(message, 'info', duration)
  }

  /**
   * 清空所有 Toast
   */
  const clearAll = (): void => {
    toasts.value = []
  }

  return {
    // 状态
    toasts,

    // 方法
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearAll
  }
}
