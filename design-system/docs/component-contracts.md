# Component Contracts

All DcoY design-system components must support:

- Semantic HTML first.
- Keyboard navigation for interactive elements.
- Visible focus states through tokenized focus rings.
- `aria-label` or labelled content where visible text is absent.
- Disabled and loading states where actions are possible.
- Dark mode by default.
- Reduced motion through global CSS and motion hooks.
- Composition over inheritance.

## Styling Rules

- Consume tokens through CSS variables or Tailwind theme mappings.
- Do not hardcode product colors in page code.
- Keep motion subtle and purposeful.
- Preserve enterprise density and avoid decorative overload.

## Data Visualization Rules

- Use shared chart colors from `chartTheme`.
- Wrap charts in `ChartContainer`.
- Use accessible labels on SVG and semantic containers.
- Avoid layout shift by giving charts stable parent dimensions.
