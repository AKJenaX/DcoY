export const breakpoints = {
  xs: 480,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536
} as const;

export const containers = {
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1200px",
  "2xl": "1440px",
  full: "100%"
} as const;

export const grid = {
  columns: 12,
  gutter: {
    mobile: "16px",
    tablet: "24px",
    desktop: "32px"
  }
} as const;
