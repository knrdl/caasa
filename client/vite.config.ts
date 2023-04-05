import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  base: '', // is "/" per default (static path) so serving from a subfolder does not work => empty base equals "./" (relative paths)
})
