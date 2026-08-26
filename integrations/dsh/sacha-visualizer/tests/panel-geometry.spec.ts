import { describe, expect, it } from 'vitest'
import {
  DEFAULT_PANEL_LAYOUT, dockPanel, floatPanel, movePanel, parsePanelLayout, resizePanel, resolvePanelLayout,
} from '../src/client/panel-geometry.ts'

const bounds = { width: 1440, height: 900, anchorRight: 1440 }

describe('panel geometry', () => {
  it('rejects corrupt persisted state and clamps valid floating state', () => {
    expect(parsePanelLayout('{')).toEqual(DEFAULT_PANEL_LAYOUT)
    const parsed = parsePanelLayout(JSON.stringify({ mode: 'floating', x: 3000, y: -20, width: 900, height: 100 }))
    expect(resolvePanelLayout(parsed, bounds)).toMatchObject({ mode: 'floating', x: 788, y: 12, width: 640, height: 360 })
  })

  it('docks against the usable right anchor and fits content height', () => {
    const docked = dockPanel(DEFAULT_PANEL_LAYOUT, bounds)
    expect(docked).toMatchObject({ mode: 'docked', x: 1034, y: 58, width: 388, heightMode: 'auto' })
    // Legacy persisted layouts lose their forced full-column height.
    expect(parsePanelLayout(JSON.stringify({ mode: 'docked', x: 0, y: 58, width: 430, height: 820 })))
      .toMatchObject({ heightMode: 'auto' })
    expect(parsePanelLayout(JSON.stringify({ mode: 'floating', x: 20, y: 20, width: 400, height: 500, heightMode: 'manual' })))
      .toMatchObject({ heightMode: 'manual' })
  })

  it('docks beside a right plugin that narrows the overlay host', () => {
    // A 400px right workbench narrows the overlay host: the dock must anchor
    // to the host's own right edge instead of sliding under the plugin layer.
    const narrowed = { width: 1040, height: 900, anchorRight: 1040 }
    expect(resolvePanelLayout(DEFAULT_PANEL_LAYOUT, narrowed)).toMatchObject({ mode: 'docked', x: 1040 - 18 - 388 })
  })

  it('moves, resizes, floats, and docks inside the host box', () => {
    const docked = dockPanel(DEFAULT_PANEL_LAYOUT, bounds)
    const floating = floatPanel(docked, bounds)
    expect(floating.mode).toBe('floating')
    expect(movePanel(floating, -5000, -5000, bounds)).toMatchObject({ x: 12, y: 12 })
    expect(resizePanel(floating, 'corner', 100, -100, bounds)).toMatchObject({ width: 488, height: 694, heightMode: 'manual' })
  })

  it('uses a safe inset overlay on compact hosts', () => {
    expect(resolvePanelLayout(DEFAULT_PANEL_LAYOUT, { width: 600, height: 700, anchorRight: 600 })).toMatchObject({
      x: 12, y: 12, width: 576, height: 676,
    })
  })
})
