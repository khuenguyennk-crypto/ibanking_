import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      '/api/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },

      '/api/users': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },

      '/api/accounts': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },

      '/api/tuitions': {
        target: 'http://localhost:8003',
        changeOrigin: true,
      },

      '/api/payments': {
        target: 'http://localhost:8004',
        changeOrigin: true,
      },
    },
  },
});
