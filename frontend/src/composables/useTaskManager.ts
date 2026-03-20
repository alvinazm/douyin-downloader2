import { ref, reactive } from 'vue'
import { ApiClient } from '@/api'
import type { CommentExportTask } from '@/types/api'

const tasks = ref<Map<string, CommentExportTask>>(new Map())
const isPolling = ref(false)
const pollInterval = ref<NodeJS.Timeout | null>(null)

export function useTaskManager() {
  /**
   * 加载所有任务
   */
  const loadAllTasks = async () => {
    try {
      const response = await ApiClient.getAllTasks()
      const tasksMap = new Map<string, CommentExportTask>()
      response.tasks.forEach(task => {
        tasksMap.set(task.task_id, task)
      })
      tasks.value = tasksMap
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
      tasks.value.set(taskId, task)
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
    if (isPolling.value) {
      return
    }

    isPolling.value = true

    pollInterval.value = setInterval(async () => {
      // 查找所有运行中的任务
      const runningTasks = Array.from(tasks.value.values()).filter(
        task => task.status === 'pending' || task.status === 'running'
      )

      if (runningTasks.length === 0) {
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
    isPolling.value = false
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
      tasks.value.delete(taskId)
    } catch (err) {
      console.error('删除任务失败:', err)
      throw err
    }
  }

  /**
   * 获取排序后的任务列表
   */
  const getSortedTasks = () => {
    return Array.from(tasks.value.values()).sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }

  /**
   * 清空所有任务
   */
  const clearAllTasks = () => {
    tasks.value.clear()
  }

  return {
    tasks,
    isPolling,
    loadAllTasks,
    getTaskStatus,
    startPolling,
    stopPolling,
    downloadTaskFile,
    deleteTask,
    getSortedTasks,
    clearAllTasks
  }
}
