/**
 * Placement math for the tool-surface hover popover.
 *
 * The panel clips its own overflow and carries a transform, so the popover is
 * portalled to the document body and positioned in viewport coordinates. Keeping
 * the arithmetic here — pure, no DOM reads — makes the flip/clamp behaviour
 * testable without a browser.
 */

/** Trigger bounds in viewport coordinates. */
export interface AnchorRect {
  readonly left: number
  readonly top: number
  readonly bottom: number
}

/** Current viewport size. */
export interface ViewportSize {
  readonly width: number
  readonly height: number
}

/** Resolved popover box. */
export interface PopoverPlacement {
  readonly left: number
  readonly top: number
  readonly width: number
  /** `above` only when the space below cannot hold the content and above is roomier. */
  readonly placement: 'below' | 'above'
  /** Content taller than this scrolls inside the popover. */
  readonly maxHeight: number
}

/** Widest the popover may grow; narrower viewports shrink it. */
export const POPOVER_MAX_WIDTH = 380
/** Smallest gap kept between the popover and any viewport edge. */
export const POPOVER_MARGIN = 12
/** Gap between the trigger and the popover. */
export const POPOVER_GAP = 6
/** Floor for the scrollable area, so a cramped viewport still shows something. */
export const POPOVER_MIN_HEIGHT = 120

/**
 * Place the popover against its trigger: clamped horizontally into the viewport,
 * below the trigger when it fits, otherwise above when that side is roomier.
 * @param anchor - trigger bounds in viewport coordinates.
 * @param contentHeight - the popover's natural height before clamping.
 * @param viewport - current viewport size.
 * @returns the resolved box, including the height at which content scrolls.
 */
export function placePopover(
  anchor: AnchorRect,
  contentHeight: number,
  viewport: ViewportSize,
): PopoverPlacement {
  const width = Math.min(POPOVER_MAX_WIDTH, Math.max(0, viewport.width - POPOVER_MARGIN * 2))
  const maxLeft = Math.max(POPOVER_MARGIN, viewport.width - width - POPOVER_MARGIN)
  const left = Math.min(Math.max(anchor.left, POPOVER_MARGIN), maxLeft)

  const spaceBelow = viewport.height - anchor.bottom - POPOVER_GAP - POPOVER_MARGIN
  const spaceAbove = anchor.top - POPOVER_GAP - POPOVER_MARGIN
  const placement: PopoverPlacement['placement'] =
    spaceBelow >= contentHeight || spaceBelow >= spaceAbove ? 'below' : 'above'

  const available = Math.max(POPOVER_MIN_HEIGHT, placement === 'below' ? spaceBelow : spaceAbove)
  const maxHeight = available
  const height = Math.min(contentHeight, maxHeight)
  const top = placement === 'below'
    ? anchor.bottom + POPOVER_GAP
    : Math.max(POPOVER_MARGIN, anchor.top - POPOVER_GAP - height)

  return { left, top, width, placement, maxHeight }
}
