# DcoY Enterprise Design System

This package defines the reusable UI foundation for future DcoY React, TypeScript, Tailwind, shadcn/ui, Framer Motion, and Lucide React interfaces.

The package intentionally does not redesign existing Streamlit pages. It establishes tokens, themes, motion, layouts, chart wrappers, and enterprise SOC components that future pages can consume.

## Import Order

```ts
import "@dcoy/design-system/theme";
```

## Principle

Pages should consume tokens and components from this package. They should not hardcode color, spacing, radius, elevation, motion, or chart styling values.

## Architecture

- `src/tokens`: semantic color, typography, spacing, radius, shadow, elevation, glow, and gradient values.
- `src/theme`: CSS variables, Tailwind layers, font loading, focus states, reduced-motion rules, and subtle background utilities.
- `src/components`: reusable enterprise UI and SOC-specific components.
- `src/layouts`: page shells, sections, grids, split panels, and widget grids.
- `src/animations`: Framer Motion presets and timing tokens.
- `src/backgrounds`: subtle product background layers, node network, glows, and particles.
- `src/data-viz`: chart containers and shared visualization primitives.
- `src/hooks`: interaction and accessibility hooks.
- `src/providers`: design-system context and reduced-motion propagation.

## Readiness Rule

Future DcoY frontend work should import from this package before creating local UI primitives.
