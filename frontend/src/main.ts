import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useConfigStore } from './stores/config'
import './style.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)
  app.use(router)

  // 加载配置
  const configStore = useConfigStore()
  await configStore.loadConfig()

  app.mount('#app')
}

bootstrap().catch(console.error)
