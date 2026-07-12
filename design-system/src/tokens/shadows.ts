export const shadows = {
  card: "0 1px 0 rgba(255,255,255,0.04) inset, 0 16px 48px rgba(0,0,0,0.28)",
  hover: "0 1px 0 rgba(255,255,255,0.05) inset, 0 24px 72px rgba(0,0,0,0.36)",
  modal: "0 1px 0 rgba(255,255,255,0.06) inset, 0 32px 96px rgba(0,0,0,0.52)",
  popover: "0 1px 0 rgba(255,255,255,0.05) inset, 0 20px 64px rgba(0,0,0,0.42)",
  glow: "0 0 0 1px rgba(59,130,246,0.18), 0 0 42px rgba(59,130,246,0.16)"
} as const;

export const elevation = {
  0: "none",
  1: shadows.card,
  2: shadows.hover,
  3: shadows.popover,
  4: shadows.modal
} as const;
