import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { defineConfig, type Plugin } from 'vite'

const ASSET_NAMES = ['cat-sacha-base.png', 'cat-jojo-base.png'] as const
const ASSET_ALLOWLIST = new Set<string>(ASSET_NAMES)
const artworkPlugin: Plugin = {
  name: 'sacha-visualizer-preview-artwork',
  configureServer(server) {
    server.middlewares.use('/plugins/sacha-visualizer/assets', async (request, response) => {
      let filename = ''
      try {
        filename = decodeURIComponent(request.url?.split('/').pop()?.split('?')[0] ?? '')
      } catch {
        response.statusCode = 404
        response.end()
        return
      }
      if (!ASSET_ALLOWLIST.has(filename)) {
        response.statusCode = 404
        response.end()
        return
      }
      response.setHeader('content-type', 'image/png')
      response.end(await readFile(new URL(`../assets/cats/${filename}`, import.meta.url)))
    })
  },
  async generateBundle() {
    for (const filename of ASSET_NAMES) {
      this.emitFile({
        type: 'asset',
        fileName: `plugins/sacha-visualizer/assets/${filename}`,
        source: await readFile(new URL(`../assets/cats/${filename}`, import.meta.url)),
      })
    }
  },
}

export default defineConfig({
  root: fileURLToPath(new URL('./', import.meta.url)),
  plugins: [artworkPlugin],
  esbuild: {
    jsx: 'automatic',
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    host: '127.0.0.1',
    port: 4176,
    strictPort: true,
  },
})
