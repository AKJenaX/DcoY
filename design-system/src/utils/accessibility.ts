import type { KeyboardEvent } from "react";

export const focusRing =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-background";

export function getAriaDisabled(disabled?: boolean, loading?: boolean) {
  return disabled || loading ? true : undefined;
}

export function onKeyboardActivate(event: KeyboardEvent, action: () => void) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    action();
  }
}
