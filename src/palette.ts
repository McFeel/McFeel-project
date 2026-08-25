export interface Swatch {
  hex: string
  name: string
}

const NAMES = [
  'Aurora',
  'Coral',
  'Slate',
  'Meadow',
  'Amber',
  'Indigo',
  'Blush',
  'Teal',
  'Sand',
  'Plum',
]

function hslToHex(h: number, s: number, l: number): string {
  const a = (s * Math.min(l, 1 - l)) / 100
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * color)
      .toString(16)
      .padStart(2, '0')
  }
  return `#${f(0)}${f(8)}${f(4)}`.toUpperCase()
}

// Build a harmonious palette from a random base hue using an analogous scheme.
export function generatePalette(count = 5): Swatch[] {
  const baseHue = Math.floor(Math.random() * 360)
  const step = 24
  return Array.from({ length: count }, (_, i) => {
    const hue = (baseHue + i * step) % 360
    const sat = 62 + ((i * 7) % 18)
    const light = 42 + i * 8
    return {
      hex: hslToHex(hue, sat, light / 100),
      name: NAMES[(baseHue + i) % NAMES.length],
    }
  })
}
