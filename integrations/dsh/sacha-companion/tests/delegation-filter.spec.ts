import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

/**
 * `cordis.patch.yml` decides each child surface's `toolFilter`, and a mistake there
 * stays invisible until a delegation is actually attempted: `tools.restrict()`
 * rejects the WHOLE filter on its first unnameable entry, so one bad name aborts
 * surface creation instead of merely narrowing the surface. These assertions pin
 * the rules that a shipped mistake violated — `sacha_worker` could not be created
 * at all while its deny list named `subagent` and `workflow`.
 */
const patch = readFileSync(fileURLToPath(new URL('../cordis.patch.yml', import.meta.url)), 'utf8')

/**
 * Names a host-plane patch must never write into a `toolFilter`, for two distinct
 * reasons:
 *
 * - `subagent` cannot be named by `tools.restrict()` in the surface's child scope:
 *   `restrict()` validates against `restrictableNames`, which holds only INHERITED
 *   names. A scope's own registrations stay visible and count as known, but are not
 *   restrictable. Measured on this Runtime: the child scope sees `subagent` in
 *   `request/header.tools`, yet `restrict({ deny: ['subagent'] })` throws there.
 * - `workflow` is `disabled` by the `ptc` preset, so naming it is not portable.
 */
const UNSAFE_FILTER_NAMES = ['subagent', 'workflow']

/** The three Sacha surfaces; a child must never gain a sibling dispatch surface. */
const SACHA_SURFACES = ['sacha_research', 'sacha_worker', 'sacha_review']

/** Extract one `- id:` row from the patch's `insert` list, indentation-agnostic. */
function row(id: string): string {
  const lines = patch.split(/\r?\n/)
  const start = lines.findIndex(line => line.trim() === `- id: ${id}`)
  if (start < 0) throw new Error(`cordis.patch.yml has no row "${id}"`)
  const rest = lines.slice(start + 1)
  const end = rest.findIndex(line => line.trim().startsWith('- id: '))
  return (end < 0 ? rest : rest.slice(0, end)).join('\n')
}

/** Names listed under a `toolFilter`'s `allow:` or `deny:` key. */
function filterNames(body: string, key: 'allow' | 'deny'): string[] {
  const block = new RegExp(`\\n\\s*${key}:\\n((?:\\s*- \\S+\\r?\\n?)+)`).exec(body)
  if (block === null) return []
  return [...block[1].matchAll(/- (\S+)/g)].map(match => match[1])
}

const SURFACE_ROWS = ['sacha-research-posix', 'sacha-research-windows', 'sacha-worker', 'sacha-review-posix', 'sacha-review-windows']

describe('child surface tool filters', () => {
  it('never names an unnameable or sibling Sacha tool', () => {
    const forbidden = new Set([...UNSAFE_FILTER_NAMES, ...SACHA_SURFACES])
    for (const id of SURFACE_ROWS) {
      const body = row(id)
      for (const key of ['allow', 'deny'] as const) {
        const named = filterNames(body, key)
        const offending = named.filter(name => forbidden.has(name))
        // One unknown name makes restrict() throw, so the surface cannot be created at all.
        expect(offending, `${id} ${key} names ${offending.join(', ')}`).toEqual([])
      }
    }
  })

  it('denies only the fork surface on sacha_worker, which every supported preset registers', () => {
    expect(filterNames(row('sacha-worker'), 'deny')).toEqual(['subagent_fork'])
  })

  it('caps every surface at one delegation layer', () => {
    // maxDepth is what enforces Sacha's single-layer dispatch once the unnameable
    // deny entries are gone; losing it would leave nesting unbounded.
    for (const id of SURFACE_ROWS) {
      expect(row(id), id).toMatch(/^\s*maxDepth: 1\s*$/m)
    }
  })
})
