import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// 引入Element Plus自动导入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    // 自动导入Element Plus组件和API
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  // 配置跨域代理（对接后端Django服务）
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // Django后端地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    }
  }
})