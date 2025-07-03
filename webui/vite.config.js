import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  base: '/',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    strictPort: true,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'webui.bit-team-bot.online',
      'api.bit-team-bot.online'
    ],
    cors: {
      origin: [
        'https://webui.bit-team-bot.online',
        'https://t.me',
        'https://web.telegram.org'
      ],
      credentials: true
    },
    proxy: {
      '/api': {
        target: 'https://api.bit-team-bot.online',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    headers: {
      'X-Frame-Options': 'ALLOWALL',
      'Content-Security-Policy': "frame-ancestors 'self' https://t.me https://web.telegram.org",
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer-when-downgrade'
    }
  }
})
