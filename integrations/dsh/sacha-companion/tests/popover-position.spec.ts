import { describe, expect, it } from 'vitest'
import {
  POPOVER_GAP, POPOVER_MARGIN, POPOVER_MAX_WIDTH, POPOVER_MIN_HEIGHT, placePopover,
} from '../src/client/popover-position.ts'

const viewport = { width: 1440, height: 900 }

describe('tool-surface popover placement', () => {
  it('sits below the trigger when there is room', () => {
    const placed = placePopover({ left: 200, top: 100, bottom: 130 }, 300, viewport)
    expect(placed.placement).toBe('below')
    expect(placed.top).toBe(130 + POPOVER_GAP)
  })

  it('flips above when the space below cannot hold the content', () => {
    const placed = placePopover({ left: 200, top: 820, bottom: 860 }, 300, viewport)
    expect(placed.placement).toBe('above')
    expect(placed.top).toBeLessThan(820)
    expect(placed.top).toBeGreaterThanOrEqual(POPOVER_MARGIN)
  })

  it('clamps into the viewport instead of overflowing the right edge', () => {
    const placed = placePopover({ left: viewport.width - 20, top: 100, bottom: 130 }, 200, viewport)
    expect(placed.left + placed.width).toBeLessThanOrEqual(viewport.width - POPOVER_MARGIN)
  })

  it('clamps into the viewport instead of overflowing the left edge', () => {
    const placed = placePopover({ left: -50, top: 100, bottom: 130 }, 200, viewport)
    expect(placed.left).toBeGreaterThanOrEqual(POPOVER_MARGIN)
  })

  it('narrows on a viewport narrower than the preferred width', () => {
    const narrow = { width: 320, height: 700 }
    const placed = placePopover({ left: 10, top: 100, bottom: 130 }, 200, narrow)
    expect(placed.width).toBeLessThanOrEqual(POPOVER_MAX_WIDTH)
    expect(placed.left + placed.width).toBeLessThanOrEqual(narrow.width)
  })

  it('caps the scrollable height to the chosen side and keeps a usable floor', () => {
    const cramped = placePopover({ left: 200, top: 880, bottom: 895 }, 900, { width: 1440, height: 900 })
    expect(cramped.maxHeight).toBeGreaterThanOrEqual(POPOVER_MIN_HEIGHT)
  })
})
