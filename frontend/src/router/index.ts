import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainView from '@/components/MainView.vue'
import VideoPreview from '@/components/VideoPreview.vue'
import CommentExport from '@/components/CommentExport.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: MainView
  },
  {
    path: '/parse',
    name: 'parse',
    component: () => import('@/components/ParsePage.vue')
  },
  {
    path: '/export/:platform',
    name: 'export',
    component: () => import('@/components/ExportPage.vue'),
    props: true
  },
  {
    path: '/download-history',
    name: 'download-history',
    component: () => import('@/components/DownloadHistory.vue'),
    meta: { requiresLoad: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
