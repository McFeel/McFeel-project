import { useEffect, useState } from 'react'
import { generatePalette, type Swatch } from './palette'
import './App.css'

function App() {
  const [palette, setPalette] = useState<Swatch[]>([])
  const [copied, setCopied] = useState<string | null>(null)

  useEffect(() => {
    setPalette(generatePalette())
  }, [])

  const regenerate = () => {
    setPalette(generatePalette())
    setCopied(null)
  }

  const copy = async (hex: string) => {
    try {
      await navigator.clipboard.writeText(hex)
    } catch {
      // Clipboard may be unavailable; still reflect the selection in the UI.
    }
    setCopied(hex)
    window.setTimeout(() => setCopied((c) => (c === hex ? null : c)), 1600)
  }

  return (
    <div className="app">
      <header className="hero">
        <span className="badge">McFeel · Palette Studio</span>
        <h1>Design beautiful palettes in a click.</h1>
        <p>
          Generate harmonious, analogous color schemes and copy any shade to
          your clipboard. A tiny starter to prove the dev environment runs end
          to end.
        </p>
        <button className="cta" onClick={regenerate} data-testid="generate">
          Generate palette
        </button>
      </header>

      <main className="palette" data-testid="palette">
        {palette.map((swatch, i) => (
          <button
            key={`${swatch.hex}-${i}`}
            className="swatch"
            style={{ background: swatch.hex }}
            onClick={() => copy(swatch.hex)}
            aria-label={`Copy ${swatch.hex}`}
          >
            <span className="swatch-meta">
              <strong>{swatch.name}</strong>
              <code>{copied === swatch.hex ? 'Copied!' : swatch.hex}</code>
            </span>
          </button>
        ))}
      </main>

      <footer className="footer">
        Built with React + Vite + TypeScript.
      </footer>
    </div>
  )
}

export default App
