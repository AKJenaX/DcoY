export const colors = {
  background: {
    primary: "#05070A",
    surface: "#0C1016",
    card: "#121923",
    elevated: "#18212E"
  },
  brand: {
    primary: "#3B82F6",
    secondary: "#7C3AED",
    accent: "#06B6D4"
  },
  state: {
    success: "#10B981",
    warning: "#F59E0B",
    danger: "#EF4444",
    info: "#3B82F6"
  },
  border: "rgba(255,255,255,0.08)",
  text: {
    primary: "#FFFFFF",
    secondary: "#CBD5E1",
    muted: "#64748B",
    inverse: "#05070A"
  },
  overlay: {
    scrim: "rgba(5,7,10,0.72)",
    subtle: "rgba(255,255,255,0.04)",
    hover: "rgba(255,255,255,0.06)",
    active: "rgba(255,255,255,0.10)"
  }
} as const;

export type DcoYColorToken = typeof colors;
