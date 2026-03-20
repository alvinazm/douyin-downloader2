import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ApiClient } from '@/api'
import type { CommentExportTask } from '@/types/api'

const tasks = ref<CommentExportTask[]>([])
const isPolling = ref(false)
const pollInterval = ref<NodeJS.Timeout | null>(null)

export function useTaskManager() {
  /**
   * 加载所有任务
   */
  const loadAllTasks = async () => {
    try {
      console.log('开始加载任务...')
      const response = await ApiClient.getAllTasks()
      console.log('任务加载成功:', response)
      tasks.value = response.tasks
      console.log('任务列表已更新，总共:', tasks.value.length, '个任务')
      return response
    } catch (err) {
      console.error('加载任务失败:', err)
      throw err
    }
  }

  /**
   * 获取单个任务状态
   */
  const getTaskStatus = async (taskId: string): Promise<CommentExportTask | null> => {
    try {
      const task = await ApiClient.getTaskStatus(taskId)
      // 更新任务列表中的任务
      const index = tasks.value.findIndex(t => t.task_id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      }
      return task
    } catch (err) {
      console.error('获取任务状态失败:', err)
      return null
    }
  }

  /**
   * 开始轮询任务状态
   */
  const startPolling = (interval: number = 2000) => {
    if (pollInterval.value) {
      console.log('轮询已在运行中')
      return
    }

    console.log('开始轮询任务状态，间隔:', interval, 'ms')

    pollInterval.value = setInterval(async () => {
      // 查找所有运行中的任务
      const runningTasks = tasks.value.filter(
        task => task.status === 'pending' || task.status === 'running'
      )

      console.log('当前运行中的任务:', runningTasks.length, '个')

      if (runningTasks.length === 0) {
        console.log('没有运行中的任务，停止轮询')
        stopPolling()
        return
      }

      // 更新每个运行中的任务
      for (const task of runningTasks) {
        await getTaskStatus(task.task_id)
      }
    }, interval)
  }

  /**
   * 停止轮询
   */
  const stopPolling = () => {
    if (pollInterval.value) {
      clearInterval(pollInterval.value)
      pollInterval.value = null
    }
    console.log('轮询已停止')
  }

  /**
   * 下载任务文件
   */
  const downloadTaskFile = async (taskId: string, filename: string) => {
    try {
      const blob = await ApiClient.downloadTaskFile(taskId)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('下载文件失败:', err)
      throw err
    }
  }

  /**
   * 删除任务
   */
  const deleteTask = async (taskId: string, deleteFile: boolean = false) => {
    try {
      await ApiClient.deleteTask(taskId, deleteFile)
      tasks.value = tasks.value.filter(t => t.task_id !== taskId)
    } catch (err) {
      console.error('删除任务失败:', err)
      throw err
    }
  }

  /**
   * 获取排序后的任务列表
   */
  const sortedTasks = computed(() => {
    return [...tasks.value].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  /**
   * 清空所有任务
   */
  const clearAllTasks = () => {
    tasks.value = []
  }

  return {
    tasks,
    sortedTasks,
    isPolling,
    loadAllTasks,
    getTaskStatus,
    startPolling,
    stopPolling,
    downloadTaskFile,
    deleteTask,
    getSortedTasks: () => sortedTasks.value,
    clearAllTasks
  }
}
