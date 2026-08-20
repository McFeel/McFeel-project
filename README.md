# McFeel · Palette Studio

A small, modern starter app used to bootstrap the development environment for
`McFeel-project`. It generates harmonious color palettes and lets you copy any
shade to your clipboard — a designer-friendly way to prove the toolchain runs
end to end.

Built with **React + Vite + TypeScript**.

## Requirements

- Node.js 20+ (developed against Node 22)
- npm 10+

## Getting started

```bash
npm ci        # install exact, locked dependencies
npm run dev   # start the Vite dev server on http://localhost:5173
```

## Scripts

| Command             | Description                                  |
| ------------------- | -------------------------------------------- |
| `npm run dev`       | Start the Vite dev server (hot reload)       |
| `npm run build`     | Type-check and build the production bundle   |
| `npm run preview`   | Preview the production build locally         |
| `npm run lint`      | Run ESLint over the project                  |
| `npm run typecheck` | Type-check without emitting output           |

## Cloud Agent environment

`.cursor/environment.json` configures the Cursor Cloud Agent environment:

- `install`: `npm ci` restores locked dependencies after checkout.
- `terminals`: a `dev-server` terminal runs `npm run dev -- --host`.
- `ports`: exposes Vite on port `5173`.
