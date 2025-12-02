import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 导入主题样式
import './style/theme.scss'

// 创建应用实例
const app = createApp(App)

// 使用插件
app.use(store).use(router).use(ElementPlus)

// 在应用挂载前初始化用户信息
store.dispatch('initUserInfo').then(() => {
  // 初始化完成后挂载应用
  app.mount('#app')
})
