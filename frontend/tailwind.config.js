/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../design-system/src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    screens: {
      xs: "480px",
      sm: "640px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px"
    },
    extend: {
      colors: {
        background: "hsl(var(--dcoy-color-bg-primary) / <alpha-value>)",
        surface: "hsl(var(--dcoy-color-surface) / <alpha-value>)",
        card: "hsl(var(--dcoy-color-card) / <alpha-value>)",
        elevated: "hsl(var(--dcoy-color-card-elevated) / <alpha-value>)",
        primary: "hsl(var(--dcoy-color-primary) / <alpha-value>)",
        secondary: "hsl(var(--dcoy-color-secondary) / <alpha-value>)",
        accent: "hsl(var(--dcoy-color-accent) / <alpha-value>)",
        success: "hsl(var(--dcoy-color-success) / <alpha-value>)",
        warning: "hsl(var(--dcoy-color-warning) / <alpha-value>)",
        danger: "hsl(var(--dcoy-color-danger) / <alpha-value>)",
        border: "hsl(var(--dcoy-color-border) / <alpha-value>)",
        foreground: "hsl(var(--dcoy-color-text-primary) / <alpha-value>)",
        muted: "hsl(var(--dcoy-color-muted) / <alpha-value>)"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"]
      },
      borderRadius: {
        ds: "var(--dcoy-radius-md)",
        "ds-lg": "var(--dcoy-radius-lg)",
        "ds-xl": "var(--dcoy-radius-xl)",
        "ds-2xl": "var(--dcoy-radius-2xl)"
      },
      boxShadow: {
        card: "var(--dcoy-shadow-card)",
        hover: "var(--dcoy-shadow-hover)",
        modal: "var(--dcoy-shadow-modal)",
        popover: "var(--dcoy-shadow-popover)",
        glow: "var(--dcoy-shadow-glow)"
      },
      backgroundImage: {
        "gradient-blue-indigo": "var(--dcoy-gradient-blue-indigo)",
        "gradient-blue-purple": "var(--dcoy-gradient-blue-purple)",
        "gradient-purple-indigo": "var(--dcoy-gradient-purple-indigo)",
        "enterprise-grid": "var(--dcoy-bg-grid)"
      },
      transitionTimingFunction: {
        spring: "cubic-bezier(0.16, 1, 0.3, 1)"
      }
    }
  },
  plugins: []
}
