export const gradients = {
  blueIndigo: "linear-gradient(135deg, #3B82F6 0%, #4F46E5 100%)",
  bluePurple: "linear-gradient(135deg, #3B82F6 0%, #7C3AED 100%)",
  purpleIndigo: "linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)",
  surface: "linear-gradient(180deg, rgba(255,255,255,0.035) 0%, rgba(255,255,255,0.01) 100%)",
  spotlight: "radial-gradient(circle at var(--spotlight-x, 50%) var(--spotlight-y, 50%), rgba(59,130,246,0.12), transparent 34rem)"
} as const;

export const glows = {
  primary: "0 0 40px rgba(59,130,246,0.18)",
  secondary: "0 0 40px rgba(124,58,237,0.16)",
  accent: "0 0 40px rgba(6,182,212,0.14)",
  danger: "0 0 34px rgba(239,68,68,0.12)"
} as const;
