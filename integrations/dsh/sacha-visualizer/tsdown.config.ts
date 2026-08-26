import { existsSync, readFileSync } from 'node:fs'
import { basename, dirname, resolve as resolvePath, sep } from 'node:path'
import { transform } from 'lightningcss'
import { defineConfig, type UserConfig } from 'tsdown'

const PLATFORM_MODULES = [
  'react', 'react/jsx-runtime', '@deepseek-ai/cordis', '@deepseek-ai/dsh-client-ui-slots',
]
const PRELOADED_CLIENT_EXTERNALS = ['@deepseek-ai/dsh-client-runtime/client']
const CLIENT_EXTERNALS: readonly string[] = [...PLATFORM_MODULES, ...PRELOADED_CLIENT_EXTERNALS]
const INLINE_SAFE = /^@deepseek-ai\/dsh-(session|llm|tools|brand)(\/|$)/
const VENDORED_LIBRARY = /^@deepseek-ai\/(cosmokit|schemastery)(\/|$)/
const GENERATED_REMOTE = /^@deepseek-ai\/dsh-[a-z0-9]+(?:-[a-z0-9]+)*\/remote$/
const CSS_VIRTUAL_PREFIX = '\0dsh-css:'
const CSS_VIRTUAL_SUFFIX = '.mjs'
const PLUGIN_ID: string = JSON.parse(
  readFileSync(new URL('./package.json', import.meta.url), 'utf8'),
).name

const config: UserConfig = {
  name: `${PLUGIN_ID}/client`,
  entry: { client: 'lib/client/index.js' },
  outDir: 'lib',
  format: 'cjs',
  platform: 'browser',
  dts: false,
  sourcemap: true,
  clean: false,
  deps: {
    neverBundle: (id: string) => CLIENT_EXTERNALS.includes(id),
    alwaysBundle: (id: string) => !CLIENT_EXTERNALS.includes(id),
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV ?? 'production'),
    'import.meta.env.MODE': JSON.stringify(process.env.NODE_ENV ?? 'production'),
    'import.meta.env': JSON.stringify({ MODE: process.env.NODE_ENV ?? 'production' }),
  },
  plugins: [{
    name: 'dsh-client-bundle-purity',
    resolveId(source: string) {
      if (!source.startsWith('@deepseek-ai/')) return null
      if (CLIENT_EXTERNALS.includes(source)) return null
      if (VENDORED_LIBRARY.test(source) || INLINE_SAFE.test(source) || GENERATED_REMOTE.test(source)) return null
      throw new Error(`client bundle purity rejected cross-plugin value import "${source}"`)
    },
  }, {
    name: 'dsh-css-modules-inline',
    resolveId(source: string, importer: string | undefined) {
      if (!source.endsWith('.module.css')) return null
      const absolute = importer === undefined ? source : sourceAssetPath(source, importer)
      return CSS_VIRTUAL_PREFIX + absolute + CSS_VIRTUAL_SUFFIX
    },
    load(virtualId: string) {
      if (!virtualId.startsWith(CSS_VIRTUAL_PREFIX)) return null
      const fileId = virtualId.slice(CSS_VIRTUAL_PREFIX.length, -CSS_VIRTUAL_SUFFIX.length)
      this.addWatchFile(fileId)
      const { code, exports: cssExports } = transform({
        filename: fileId,
        code: readFileSync(fileId),
        cssModules: { pattern: '[hash]_[local]' },
        minify: true,
      })
      const classMap: Record<string, string> = {}
      for (const [local, value] of Object.entries(cssExports ?? {}).sort(([left], [right]) => left.localeCompare(right))) {
        classMap[local] = value.name
      }
      const tagId = `${PLUGIN_ID}/${basename(fileId)}`
      return [
        `const css = ${JSON.stringify(code.toString())};`,
        `const tagId = ${JSON.stringify(tagId)};`,
        'if (typeof document !== "undefined" && document.querySelector(`style[data-plugin-css="${tagId}"]`) === null) {',
        '  const tag = document.createElement("style");',
        `  tag.dataset.plugin = ${JSON.stringify(PLUGIN_ID)};`,
        '  tag.dataset.pluginCss = tagId;',
        '  tag.textContent = css;',
        '  document.head.appendChild(tag);',
        '}',
        `export default ${JSON.stringify(classMap)};`,
      ].join('\n')
    },
  }],
  outputOptions: {
    entryFileNames: 'client.js',
    banner: `window.__ModuleLoader__.load({ id: ${JSON.stringify(PLUGIN_ID)}, factory: (require) => {`,
    footer: 'return module.exports; } });',
    intro: 'var module = { exports: {} }; var exports = module.exports;',
  },
}

function sourceAssetPath(source: string, importer: string): string {
  const emitted = resolvePath(dirname(importer), source)
  if (existsSync(emitted)) return emitted
  const marker = `${sep}lib${sep}`
  const index = emitted.indexOf(marker)
  if (index === -1) return source
  const candidate = `${emitted.slice(0, index)}${sep}src${sep}${emitted.slice(index + marker.length)}`
  return existsSync(candidate) ? candidate : source
}

export default defineConfig(config)

