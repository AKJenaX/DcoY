import { useEffect } from "react";

export function useKeyboardShortcut(keys: string[], callback: () => void, enabled = true) {
  useEffect(() => {
    if (!enabled) return undefined;
    const normalized = keys.map((key) => key.toLowerCase());
    const handler = (event: KeyboardEvent) => {
      const pressed = [
        event.metaKey ? "meta" : "",
        event.ctrlKey ? "ctrl" : "",
        event.altKey ? "alt" : "",
        event.shiftKey ? "shift" : "",
        event.key.toLowerCase()
      ].filter(Boolean);
      if (normalized.every((key) => pressed.includes(key))) {
        event.preventDefault();
        callback();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [callback, enabled, keys]);
}
