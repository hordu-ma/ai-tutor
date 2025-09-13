import { createApp } from 'vue'
import router from '@/router'
import App from './App.vue'

// Element Plus styles (only import base styles for auto-import mode)
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(router)

app.mount('#app')
