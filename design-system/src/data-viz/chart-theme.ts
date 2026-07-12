import { colors } from "../tokens";

export const chartTheme = {
  colors: {
    primary: colors.brand.primary,
    secondary: colors.brand.secondary,
    accent: colors.brand.accent,
    success: colors.state.success,
    warning: colors.state.warning,
    danger: colors.state.danger,
    muted: colors.text.muted,
    grid: colors.border,
    text: colors.text.secondary
  },
  margin: { top: 20, right: 20, bottom: 28, left: 32 }
} as const;
