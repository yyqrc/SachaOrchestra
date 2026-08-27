/**
 * Cat Role artwork combines small raster base portraits with inline SVG props.
 * Sacha and Jojo share the same front-facing composition, while Role and state
 * details remain crisp and animated at the actual 20-44px display sizes.
 *
 * Animation: the outer panel CSS transforms the whole sticker; props remain
 * vector overlays so small role and state changes stay readable.
 */

import type { JSX } from 'react'

export type CatKind = 'sacha' | 'jojo'

export interface CatProps {
  readonly kind: CatKind
  /** Role prop drawn at the lower-right of the head. */
  readonly prop?: CatProp
  readonly size?: number
  readonly title?: string
}

export type CatProp =
  | 'none' | 'conductor' | 'explore' | 'research' | 'engineer' | 'security' | 'docs' | 'data'
  | 'operator' | 'design' | 'qa' | 'working' | 'sleeping' | 'thinking'

/* --- palette ----------------------------------------------------------- */

interface CatPalette {
  readonly fur: string
  readonly furShade: string
  readonly point: string
  readonly pointShade: string
  readonly innerEar: string
  readonly eye: string
  readonly eyeDeep: string
  readonly eyeGlow: string
  readonly nose: string
  readonly muzzle: string
  readonly shoulder: string
  readonly marking: string
  readonly markingSoft: string
  readonly outline: string
}

const RAGDOLL: CatPalette = {
  fur: '#fff2df',
  furShade: '#ead5bb',
  point: '#b09a8b',
  pointShade: '#80675a',
  innerEar: '#efa99a',
  eye: '#3f9ddd',
  eyeDeep: '#245b91',
  eyeGlow: '#9ddcff',
  nose: '#df7775',
  muzzle: '#fff8e9',
  shoulder: '#f5dfc3',
  marking: '#967d70',
  markingSoft: '#c5afa2',
  outline: '#54382b',
}

const SHORTHAIR: CatPalette = {
  fur: '#ddd8d0',
  furShade: '#c2bbb2',
  point: '#8f8881',
  pointShade: '#625a54',
  innerEar: '#efb2a7',
  eye: '#aeb83d',
  eyeDeep: '#596727',
  eyeGlow: '#e9dc53',
  nose: '#d27c7d',
  muzzle: '#f5eee5',
  shoulder: '#d1cbc2',
  marking: '#827b75',
  markingSoft: '#aaa39c',
  outline: '#51382c',
}

const MICRO_MOTION = `
  .cat-base-art {
    filter: drop-shadow(0 1px 1px rgba(70, 54, 47, .18));
  }
  .cat-prop-art {
    filter: drop-shadow(.7px .9px 0 rgba(70, 54, 47, .2));
  }
  .cat-role-prop {
    transform-box: view-box;
    transform-origin: 47px 50px;
    transform: translate(var(--cat-prop-offset-x, 9px), var(--cat-prop-offset-y, -1px)) scale(var(--cat-prop-scale, .86));
  }
  .cat-prop-paw {
    filter: drop-shadow(.5px .7px 0 rgba(70, 54, 47, .16));
  }
`

/* --- base cat ---------------------------------------------------------- */

const BASE_CAT_ASSET: Record<CatKind, string> = {
  sacha: '/plugins/sacha-visualizer/assets/cat-sacha-base.png',
  jojo: '/plugins/sacha-visualizer/assets/cat-jojo-base.png',
}

function BaseHead({ kind }: { readonly kind: CatKind }): JSX.Element {
  return (
    <image
      className="cat-base-art"
      href={BASE_CAT_ASSET[kind]}
      x="1"
      y="2"
      width="58"
      height="58"
      preserveAspectRatio="xMidYMid meet"
    />
  )
}

/* --- role props -------------------------------------------------------- */

function PropArt({ children, detached = true }: {
  readonly children: JSX.Element | readonly JSX.Element[]
  readonly detached?: boolean
}): JSX.Element {
  if (!detached) return <g className="cat-prop-art">{children}</g>
  return <g className="cat-prop-art cat-role-prop">{children}</g>
}

function PawArt(): JSX.Element {
  return (
    <g className="cat-prop-paw">
      <circle cx="43.8" cy="53" r="4.35" fill="currentColor" stroke="#5d493f" strokeWidth="1.15" />
      <ellipse cx="43.8" cy="53.65" rx="1.45" ry="1.15" fill="#b97870" opacity=".74" />
      <circle cx="41.95" cy="51.45" r=".68" fill="#b97870" opacity=".74" />
      <circle cx="43.75" cy="50.75" r=".72" fill="#b97870" opacity=".74" />
      <circle cx="45.6" cy="51.4" r=".68" fill="#b97870" opacity=".74" />
    </g>
  )
}

function ConductorProp({ color }: { readonly color: string }): JSX.Element {
  return (
    <PropArt>
      <>
        <path d="M43.2 54 L53.4 38.4" fill="none" stroke="#5d493f" strokeWidth="3.2" strokeLinecap="round" />
        <path d="M43.2 54 L53.4 38.4" fill="none" stroke="#f1dfc2" strokeWidth="1.45" strokeLinecap="round" />
        <path d="M41.3 54.8 Q43.7 56.4 45.6 53.4 L43.4 51.9 Q40.8 52.3 41.3 54.8 Z" fill={color} stroke="#5d493f" strokeWidth="1" strokeLinejoin="round" />
        <circle cx="53.6" cy="38.1" r="1" fill="#f7c85d" stroke="#5d493f" strokeWidth=".65" />
        <PawArt />
      </>
    </PropArt>
  )
}

function Prop({ kind, cat }: { readonly kind: CatProp; readonly cat: CatKind }): JSX.Element | null {
  const c = cat === 'sacha' ? RAGDOLL : SHORTHAIR

  switch (kind) {
    case 'conductor':
      return <ConductorProp color={c.pointShade} />
    case 'explore':
      return (
        <PropArt>
          <>
            <path d="M40 45 C40 41.6 42.5 39.7 45.2 39.7 C48.2 39.7 50.2 41.7 50.2 44.5 C50.2 46.3 49.1 47.4 47.8 48.2 L47.4 50 H43.3 L42.9 48.2 C41.2 47.3 40 46.1 40 45 Z" fill="#f6c95d" stroke="#6a513b" strokeWidth="1.1" strokeLinejoin="round" />
            <path d="M43.3 52 H47.5 M43.8 50 H47" stroke="#6a513b" strokeWidth="1" strokeLinecap="round" />
            <path d="M40.3 40.8 L38.8 39.3 M45.1 38.5 V36.5" stroke="#d79128" strokeWidth="1.2" strokeLinecap="round" />
            <path d="M50.2 36.8 C53.4 36.8 55.3 38.3 55.3 40.5 C55.3 42.7 53.5 43.8 51.6 43.8 L49.9 45.3 L50.2 43.2 C49.2 42.5 48.7 41.6 48.7 40.5 C48.7 38.3 49.4 36.8 50.2 36.8 Z" fill="#fff9ed" stroke={c.outline} strokeWidth=".9" />
            <path d="M51 39.1 Q53 38.4 53.1 39.9 Q53.1 40.8 52 41.2 V41.8 M52 42.8 V43" fill="none" stroke={c.eyeDeep} strokeWidth=".85" strokeLinecap="round" />
          </>
        </PropArt>
      )
    case 'research':
      return (
        <PropArt>
          <>
            <path d="M39.2 42.3 Q43.6 40.6 46.8 43 V53.5 Q43.2 51.7 39.2 52.9 Z" fill="#fff4dc" stroke={c.outline} strokeWidth="1.05" strokeLinejoin="round" />
            <path d="M46.8 43 Q50.5 40.7 54.7 42.3 V52.9 Q50.6 51.7 46.8 53.5 Z" fill="#fff9ea" stroke={c.outline} strokeWidth="1.05" strokeLinejoin="round" />
            <path d="M46.8 43 V53.5" stroke="#b89c80" strokeWidth=".85" strokeLinecap="round" />
            <path d="M41.2 45 H44.7 M41.2 47.3 H44.1 M49 45.3 H52.7 M49 47.6 H51.8" stroke="#aa927d" strokeWidth=".8" strokeLinecap="round" />
            <path d="M49.2 50.1 H53" stroke="#d99b3e" strokeWidth="1.2" strokeLinecap="round" />
            <path d="M51.2 41.2 H53.8 V44.2 L52.5 43.3 L51.2 44.2 Z" fill="#73a9cc" stroke="#4c7188" strokeWidth=".65" strokeLinejoin="round" />
          </>
        </PropArt>
      )
    case 'engineer':
      return (
        <PropArt>
          <>
            <rect x="39.6" y="41" width="14.2" height="9.6" rx="1.5" fill="#577183" stroke="#3f4d54" strokeWidth="1.1" />
            <rect x="41.3" y="42.6" width="10.8" height="6.1" rx=".65" fill="#b8e3ec" />
            <path d="M43.4 44.4 L45.8 45.7 L43.4 47 M47.2 47 H49.6" fill="none" stroke="#32657a" strokeWidth=".95" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M38.5 51.5 H54.9 L52.8 54 H40.6 Z" fill="#78909b" stroke="#3f4d54" strokeWidth="1" strokeLinejoin="round" />
          </>
        </PropArt>
      )
    case 'security':
      return (
        <PropArt>
          <>
            <rect x="39.8" y="39.7" width="12.8" height="15.3" rx="1.5" fill="#fff4d9" stroke="#72533d" strokeWidth="1.15" />
            <path d="M43 39.4 V38.4 H49.5 V41 H43 Z" fill="#a47b58" stroke="#72533d" strokeWidth=".9" strokeLinejoin="round" />
            <path d="M42.1 45 L43.7 46.5 L46 43.6" fill="none" stroke="#78a253" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="43.5" cy="50.2" r="1.2" fill="#e5a632" />
            <path d="M46.8 45 H50.1 M46.8 50.2 H50.1" stroke="#9b886f" strokeWidth="1" strokeLinecap="round" />
            <path d="M46.8 54.7 L54.9 44.1" stroke="#7b4434" strokeWidth="3" strokeLinecap="round" />
            <path d="M46.8 54.7 L54.9 44.1" stroke="#d95f4e" strokeWidth="1.65" strokeLinecap="round" />
            <path d="M46.1 55.6 L46.8 53.4 L48.2 54.5 Z" fill="#ead1aa" stroke="#7b4434" strokeWidth=".65" strokeLinejoin="round" />
          </>
        </PropArt>
      )
    case 'docs':
      return (
        <PropArt>
          <>
            <path d="M40.2 39.2 H49.3 L53.3 43.2 V54.5 H40.2 Z" fill="#fff4dc" stroke="#6f5b4d" strokeWidth="1.15" strokeLinejoin="round" />
            <path d="M49.3 39.2 V43.2 H53.3" fill="#e5d2af" stroke="#6f5b4d" strokeWidth="1" strokeLinejoin="round" />
            <path d="M42.8 46 H50.5 M42.8 49 H50.5 M42.8 52 H48.6" stroke="#aa927d" strokeWidth="1" strokeLinecap="round" />
          </>
        </PropArt>
      )
    case 'data':
      return (
        <PropArt>
          <>
            <rect x="39.4" y="39.7" width="15.1" height="14.9" rx="2.2" fill="#e5f1f2" stroke="#48656a" strokeWidth="1.15" />
            <circle cx="42.2" cy="43" r="1.15" fill="#64a4aa" />
            <path d="M44.5 43 H51.9" stroke="#7ca1a4" strokeWidth="1" strokeLinecap="round" />
            <path d="M41.5 52.1 H52.2" stroke="#48656a" strokeWidth=".85" strokeLinecap="round" />
            <rect x="42" y="48.6" width="2" height="3" rx=".45" fill="#82b5bc" />
            <rect x="45.5" y="46.5" width="2" height="5.1" rx=".45" fill="#67a2ad" />
            <rect x="49" y="44.8" width="2" height="6.8" rx=".45" fill="#4d8491" />
          </>
        </PropArt>
      )
    case 'operator':
      return (
        <PropArt>
          <>
            <g stroke={c.pointShade} strokeWidth="2.6" strokeLinecap="square">
              <path d="M47 39 V42 M47 51 V54 M40 46.5 H43 M51 46.5 H54 M42.1 41.6 L44.1 43.6 M49.9 49.4 L51.9 51.4 M42.1 51.4 L44.1 49.4 M49.9 43.6 L51.9 41.6" />
            </g>
            <circle cx="47" cy="46.5" r="5.4" fill="#a8b2b2" stroke={c.pointShade} strokeWidth="1.25" />
            <circle cx="47" cy="46.5" r="2" fill="#f8ecdc" stroke={c.pointShade} strokeWidth="1.1" />
          </>
        </PropArt>
      )
    case 'design':
      return (
        <PropArt>
          <>
            <circle cx="42.1" cy="49.9" r="2" fill="#e7777e" stroke="#6b5047" strokeWidth=".75" />
            <circle cx="46" cy="52.2" r="1.8" fill="#67a9d1" stroke="#6b5047" strokeWidth=".75" />
            <circle cx="49.5" cy="49.3" r="1.8" fill="#e7b84f" stroke="#6b5047" strokeWidth=".75" />
            <path d="M42.3 53.8 L52.8 39.7" stroke="#604b41" strokeWidth="3" strokeLinecap="round" />
            <path d="M42.3 53.8 L52.8 39.7" stroke="#d86658" strokeWidth="1.55" strokeLinecap="round" />
            <path d="M52.1 42 L53.7 38.6 L55 42.2 Z" fill="#eed2a3" stroke="#604b41" strokeWidth=".75" strokeLinejoin="round" />
            <path d="M39.8 41.2 L40.5 42.6 L42 43.2 L40.5 43.8 L39.8 45.2 L39.2 43.8 L37.7 43.2 L39.2 42.6 Z" fill="#f7d66b" stroke="#8b6d31" strokeWidth=".55" />
          </>
        </PropArt>
      )
    case 'qa':
      return (
        <PropArt>
          <>
            <path d="M41.2 42.5 H52.8 V53.2 H41.2 Z" fill="#edf3df" stroke="#5f7450" strokeWidth="1.1" strokeLinejoin="round" />
            <path d="M43.2 47.2 L45.3 49.2 L49.2 44.8" fill="none" stroke="#5f914a" strokeWidth="1.55" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M49.7 50 L53.3 53.6 M53.3 50 L49.7 53.6" stroke="#c76162" strokeWidth="1.25" strokeLinecap="round" />
            <path d="M43.5 40.2 H50.5" stroke="#5f7450" strokeWidth="2.2" strokeLinecap="round" />
          </>
        </PropArt>
      )
    case 'working':
      return (
        <PropArt detached={false}>
          <>
            <circle cx="42.3" cy="47" r="1.55" fill={c.eyeDeep} />
            <circle cx="47" cy="45.7" r="1.55" fill={c.eyeDeep} />
            <circle cx="51.7" cy="44.4" r="1.55" fill={c.eyeDeep} />
          </>
        </PropArt>
      )
    case 'sleeping':
      return (
        <PropArt detached={false}>
          <>
            <text x="41" y="51" fill={c.pointShade} fontFamily="ui-rounded, system-ui, sans-serif" fontSize="7.5" fontWeight="800">z</text>
            <text x="47" y="45.7" fill={c.pointShade} fontFamily="ui-rounded, system-ui, sans-serif" fontSize="10" fontWeight="800">Z</text>
          </>
        </PropArt>
      )
    case 'thinking':
      return (
        <PropArt detached={false}>
          <>
            <circle cx="41.6" cy="51.9" r="1.3" fill="#fff8ec" stroke={c.pointShade} strokeWidth=".9" />
            <circle cx="45.3" cy="48.2" r="2" fill="#fff8ec" stroke={c.pointShade} strokeWidth=".95" />
            <path d="M48.1 39.2 C50 38 52.7 38.6 53.5 40.4 C55.3 40.7 56 42.5 55 44 C55.8 45.9 54.4 47.6 52.5 47.6 H48.7 C46.6 47.6 45.6 45.9 46.3 44.3 C45.4 42.6 46.3 40.4 48.1 40 Z" fill="#fff8ec" stroke={c.pointShade} strokeWidth="1" strokeLinejoin="round" />
          </>
        </PropArt>
      )
    default:
      return null
  }
}

/* --- public component -------------------------------------------------- */

export function CatArt({ kind, prop = 'none', size = 44, title }: CatProps): JSX.Element {
  const label = title ?? (kind === 'sacha' ? 'Sacha（布偶猫）' : 'Jojo（美短）')
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label={label} style={{ overflow: 'visible' }}>
      <title>{label}</title>
      <style>{MICRO_MOTION}</style>
      <BaseHead kind={kind} />
      <g className="cat-prop" color={kind === 'sacha' ? RAGDOLL.shoulder : SHORTHAIR.shoulder} aria-hidden="true">
        {prop !== 'none' ? <Prop kind={prop} cat={kind} /> : null}
      </g>
    </svg>
  )
}
