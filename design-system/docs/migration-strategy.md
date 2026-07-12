# DcoY Design System Migration Strategy

This design system is a foundation package. Existing Streamlit pages should not be redesigned in the same sprint that introduces the system.

## Phase 1: Token Alignment

- Replace page-level hardcoded colors with semantic CSS variables.
- Map Streamlit theme variables to DcoY token names.
- Keep all business logic and layouts unchanged.

## Phase 2: Component Replacement

- Replace duplicated KPI cards with `StatisticCard`.
- Replace bespoke containers with `Card`, `Panel`, `SOCWidget`, and `ChartContainer`.
- Replace local badges/pills with `Badge` and `StatusPill`.
- Replace table CSS with `Table` primitives.

## Phase 3: Layout Normalization

- Move page shells to `DashboardLayout`.
- Use `PageHeader`, `SectionContainer`, `ContentGrid`, `SidebarLayout`, `SplitPanelLayout`, and `WidgetLayout`.
- Keep route structure and API calls unchanged.

## Phase 4: Motion and Interaction

- Use `motionPresets` for page transitions, dialogs, drawers, hover, and loading.
- Use `useReducedMotionPreference` for every custom animation.
- Add spotlight and hover lift only to high-value surfaces.

## Phase 5: React Frontend Adoption

- Future React pages import from `@dcoy/design-system`.
- New pages must not hardcode color, spacing, radius, shadows, chart colors, or animation durations.
- New pages must ship with keyboard navigation, focus states, and accessible labels.
