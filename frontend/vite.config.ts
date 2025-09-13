import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// Auto-import plugins
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  plugins: [
    vue(),

    // Auto-import for Vue APIs and Element Plus services like ElMessage
    AutoImport({
      // targets for auto-import
      imports: ['vue', 'vue-router'],

      // resolvers for custom rules, e.g., for Element Plus services
      resolvers: [ElementPlusResolver()],

      // file path for generating TypeScript declaration
      dts: 'src/types/auto-imports.d.ts',
    }),

    // Auto-import for Element Plus components
    Components({
      // resolvers for component libraries
      resolvers: [
        ElementPlusResolver(), // Auto-import Element Plus components
      ],

      // file path for generating TypeScript declaration
      dts: 'src/types/components.d.ts',
    }),
  ],
  server: {
    port: 6173,
    // Proxy API requests to the backend server in development
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
