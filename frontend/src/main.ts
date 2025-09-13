import { createApp } from 'vue'
import router from '@/router'
import App from './App.vue'

// Element Plus styles and locale
import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const app = createApp(App)

app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')
