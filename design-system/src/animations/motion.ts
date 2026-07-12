import type { Variants, Transition } from "framer-motion";

export const durations = {
  fast: 0.18,
  normal: 0.3,
  slow: 0.45
} as const;

export const easings = {
  standard: [0.16, 1, 0.3, 1],
  productive: [0.2, 0, 0, 1],
  expressive: [0.34, 1.56, 0.64, 1]
} as const;

export const springs = {
  subtle: { type: "spring", stiffness: 260, damping: 26, mass: 0.8 },
  interactive: { type: "spring", stiffness: 360, damping: 30, mass: 0.7 },
  modal: { type: "spring", stiffness: 220, damping: 24, mass: 0.9 }
} as const satisfies Record<string, Transition>;

export const motionPresets = {
  entrance: {
    initial: { opacity: 0, y: 12, scale: 0.98 },
    animate: { opacity: 1, y: 0, scale: 1 },
    transition: springs.subtle
  },
  exit: {
    exit: { opacity: 0, y: 8, scale: 0.98 },
    transition: { duration: durations.fast, ease: easings.productive }
  },
  hover: {
    whileHover: { y: -2, scale: 1.005 },
    transition: springs.interactive
  },
  press: {
    whileTap: { scale: 0.985 },
    transition: springs.interactive
  },
  pageTransition: {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -8 },
    transition: { duration: durations.normal, ease: easings.standard }
  },
  modal: {
    initial: { opacity: 0, scale: 0.96, y: 16 },
    animate: { opacity: 1, scale: 1, y: 0 },
    exit: { opacity: 0, scale: 0.96, y: 12 },
    transition: springs.modal
  },
  drawer: {
    initial: { opacity: 0, x: 24 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 24 },
    transition: springs.modal
  },
  loading: {
    animate: { opacity: [0.45, 1, 0.45] },
    transition: { duration: 1.4, repeat: Infinity, ease: "easeInOut" }
  }
} as const;

export const scrollReveal: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: durations.normal, ease: easings.standard }
  }
};

export function withoutMotion<T>(animated: T, fallback: T, reducedMotion?: boolean): T {
  return reducedMotion ? fallback : animated;
}
