import { createApp } from 'vue'
import App from './App.vue'
import './styles.css'
import router from './router'

const app = createApp(App)
app.use(router)     // ✅ important
app.mount('#app')