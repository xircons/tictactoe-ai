import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  // Vercel serves the app at the domain root, so base is '/'.
  // (If you still need a GitHub Pages build, set VITE_BASE=/tictactoe-ai/ in the env.)
  base: process.env.VITE_BASE || '/'
})
