import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import VueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    vue(),
    VueDevTools(),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  build: {
    // 代码分割配置
    rollupOptions: {
      output: {
        // 手动分块配置
        manualChunks: {
          // Vue 相关库
          'vue-vendor': ['vue', 'vue-router', 'pinia'],

          // Element Plus 相关
          'element-plus': ['element-plus'],

          // 图表库
          'charts': ['echarts'],

          // Excel 处理库（按需加载）
          'xlsx': ['xlsx'],

          // 工具库
          'utils': ['axios', 'lodash-es'],
        },

        // 动态导入的chunk命名
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
          if (facadeModuleId) {
            if (facadeModuleId.includes('node_modules')) {
              return 'vendor/[name]-[hash].js'
            }
            if (facadeModuleId.includes('src/views/')) {
              return 'views/[name]-[hash].js'
            }
            if (facadeModuleId.includes('src/components/')) {
              return 'components/[name]-[hash].js'
            }
          }
          return 'chunks/[name]-[hash].js'
        },

        // 静态资源命名
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/\.(css)$/.test(assetInfo.name)) {
            return 'css/[name]-[hash].[ext]'
          }
          if (/\.(png|jpe?g|gif|svg|ico|webp)$/.test(assetInfo.name)) {
            return 'images/[name]-[hash].[ext]'
          }
          return 'assets/[name]-[hash].[ext]'
        },
      },
    },

    // 调整chunk大小警告限制
    chunkSizeWarningLimit: 1000,

    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        // 移除console和debugger
        drop_console: true,
        drop_debugger: true,
      },
    },

    // 分析模式配置
    ...(mode === 'analyze' && {
      rollupOptions: {
        output: {
          manualChunks: undefined, // 禁用手动分块以便分析
        },
      },
    }),
  },
}))
