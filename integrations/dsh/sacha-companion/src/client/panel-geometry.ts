/** Pure persisted geometry for the Sacha shell-overlay panel. */

export type PanelMode = 'docked' | 'floating'
export type PanelHeightMode = 'auto' | 'manual'
export type PanelResizeEdge = 'left' | 'bottom' | 'corner'

export interface PanelLayout {
  readonly mode: PanelMode
  readonly x: number
  readonly y: number
  readonly width: number
  readonly height: number
  readonly heightMode: PanelHeightMode
}

/** The overlay host box plus the right edge the dock anchors to. */
export interface PanelBounds {
  readonly width: number
  readonly height: number
  readonly anchorRight: number
}

export const PANEL_LAYOUT_STORAGE_KEY = 'sacha-visualizer:panel-layout:v1'
export const PANEL_COMPACT_BREAKPOINT = 960
export const PANEL_DEFAULT_WIDTH = 388
export const PANEL_DEFAULT_HEIGHT = 640
export const DEFAULT_PANEL_LAYOUT: PanelLayout = Object.freeze({
  mode: 'docked',
  x: 0,
  y: 58,
  width: PANEL_DEFAULT_WIDTH,
  height: PANEL_DEFAULT_HEIGHT,
  heightMode: 'auto',
})
const MIN_WIDTH = 320
const MAX_WIDTH = 640
const MIN_HEIGHT = 360
const DOCK_TOP = 58
const DOCK_RIGHT = 18
const DOCK_BOTTOM = 48
const FLOAT_MARGIN = 12

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(Math.max(value, minimum), maximum)
}

function finite(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

/** Decode one complete persisted layout; corrupt values restore defaults. */
export function parsePanelLayout(value: string | null): PanelLayout {
  if (value === null) return DEFAULT_PANEL_LAYOUT
  try {
    const parsed: unknown = JSON.parse(value)
    if (typeof parsed !== 'object' || parsed === null) return DEFAULT_PANEL_LAYOUT
    const record = parsed as Record<string, unknown>
    if ((record.mode !== 'docked' && record.mode !== 'floating')
      || !finite(record.x) || !finite(record.y) || !finite(record.width) || !finite(record.height)) {
      return DEFAULT_PANEL_LAYOUT
    }
    return {
      mode: record.mode,
      x: record.x,
      y: record.y,
      width: record.width,
      height: record.height,
      // Legacy persisted layouts predate content-fit height; treat them as
      // automatic so the upgrade drops the old full-column height.
      heightMode: record.mode === 'floating' && record.heightMode === 'manual' ? 'manual' : 'auto',
    }
  } catch {
    return DEFAULT_PANEL_LAYOUT
  }
}

export function compactPanel(bounds: PanelBounds): boolean {
  return bounds.width <= PANEL_COMPACT_BREAKPOINT
}

/** Docked and compact panels fit their content; only manual floating panels keep a stored height. */
export function panelUsesAutoHeight(layout: PanelLayout, bounds: PanelBounds): boolean {
  return compactPanel(bounds) || layout.mode === 'docked' || layout.heightMode === 'auto'
}

/** CSS max-height ceiling that keeps an auto-height panel inside its host. */
export function panelMaximumHeight(layout: PanelLayout, bounds: PanelBounds): number {
  const bottomInset = compactPanel(bounds) || layout.mode === 'floating' ? FLOAT_MARGIN : DOCK_BOTTOM
  return Math.max(1, bounds.height - layout.y - bottomInset)
}

/** Clamp persisted state into the current host box. */
export function resolvePanelLayout(layout: PanelLayout, bounds: PanelBounds): PanelLayout {
  const boundsWidth = Math.max(1, bounds.width)
  const boundsHeight = Math.max(1, bounds.height)
  if (compactPanel(bounds)) {
    return {
      ...layout,
      x: FLOAT_MARGIN,
      y: FLOAT_MARGIN,
      width: boundsWidth - FLOAT_MARGIN * 2,
      height: boundsHeight - FLOAT_MARGIN * 2,
    }
  }
  const widthLimit = Math.max(1, boundsWidth - FLOAT_MARGIN * 2)
  const width = clamp(layout.width, Math.min(MIN_WIDTH, widthLimit), Math.min(MAX_WIDTH, widthLimit))
  const heightLimit = Math.max(1, boundsHeight - FLOAT_MARGIN * 2)
  if (layout.mode === 'docked') {
    const availableHeight = Math.max(1, boundsHeight - DOCK_TOP - DOCK_BOTTOM)
    const anchorRight = clamp(bounds.anchorRight, 0, boundsWidth)
    const maximumX = Math.max(FLOAT_MARGIN, boundsWidth - width - FLOAT_MARGIN)
    return {
      mode: 'docked',
      x: clamp(anchorRight - DOCK_RIGHT - width, FLOAT_MARGIN, maximumX),
      y: DOCK_TOP,
      width,
      height: availableHeight,
      heightMode: layout.heightMode,
    }
  }
  const height = clamp(layout.height, Math.min(MIN_HEIGHT, heightLimit), heightLimit)
  return {
    mode: 'floating',
    x: clamp(layout.x, FLOAT_MARGIN, Math.max(FLOAT_MARGIN, boundsWidth - width - FLOAT_MARGIN)),
    y: clamp(layout.y, FLOAT_MARGIN, Math.max(FLOAT_MARGIN, boundsHeight - height - FLOAT_MARGIN)),
    width,
    height,
    heightMode: layout.heightMode,
  }
}

export function floatPanel(layout: PanelLayout, bounds: PanelBounds): PanelLayout {
  const resolved = resolvePanelLayout(layout, bounds)
  return resolvePanelLayout({ ...resolved, mode: 'floating' }, bounds)
}

/** Return to the right dock, restoring content-fit height. */
export function dockPanel(layout: PanelLayout, bounds: PanelBounds): PanelLayout {
  return resolvePanelLayout({ ...layout, mode: 'docked', heightMode: 'auto' }, bounds)
}

export function movePanel(layout: PanelLayout, dx: number, dy: number, bounds: PanelBounds): PanelLayout {
  const floating = floatPanel(layout, bounds)
  return resolvePanelLayout({ ...floating, x: floating.x + dx, y: floating.y + dy }, bounds)
}

/** Resize while preserving the edge opposite the active handle. */
export function resizePanel(
  layout: PanelLayout,
  edge: PanelResizeEdge,
  dx: number,
  dy: number,
  bounds: PanelBounds,
): PanelLayout {
  const resolved = resolvePanelLayout(layout, bounds)
  if (resolved.mode === 'docked') {
    if (edge !== 'left') return resolved
    return resolvePanelLayout({ ...resolved, width: resolved.width - dx }, bounds)
  }
  if (edge === 'left') {
    const right = resolved.x + resolved.width
    const candidate = resolvePanelLayout({ ...resolved, width: resolved.width - dx }, bounds)
    return resolvePanelLayout({ ...candidate, x: right - candidate.width }, bounds)
  }
  if (edge === 'bottom') {
    return resolvePanelLayout({ ...resolved, height: resolved.height + dy, heightMode: 'manual' }, bounds)
  }
  return resolvePanelLayout({ ...resolved, width: resolved.width + dx, height: resolved.height + dy, heightMode: 'manual' }, bounds)
}
