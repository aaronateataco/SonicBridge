import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Direct proxy: any request starting with /stations goes to backend
      '/stations': {
        target: 'http://127.0.0.1:5173', // Put your backend URL/port here (usually 5000 or 8000)
        changeOrigin: true,
        secure: false,
      },
      // Alternative: If you want to proxy all endpoints starting with /api
      /*
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // removes /api prefix before forwarding
      }
      */
    }
  }
})
