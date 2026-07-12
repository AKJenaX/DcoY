import { createContext, useContext, useMemo, type ReactNode } from "react";
import { useReducedMotionPreference } from "../hooks";
import "../theme/dcoy.css";

type DesignSystemContextValue = {
  reducedMotion: boolean;
  density: "comfortable" | "compact";
};

const DesignSystemContext = createContext<DesignSystemContextValue | null>(null);

export function DesignSystemProvider({
  children,
  density = "comfortable"
}: {
  children: ReactNode;
  density?: "comfortable" | "compact";
}) {
  const reducedMotion = useReducedMotionPreference();
  const value = useMemo(() => ({ reducedMotion, density }), [density, reducedMotion]);

  return (
    <DesignSystemContext.Provider value={value}>
      <div data-theme="dark" data-density={density} className={reducedMotion ? "dcoy-reduced-motion" : undefined}>
        {children}
      </div>
    </DesignSystemContext.Provider>
  );
}

export function useDesignSystem() {
  const context = useContext(DesignSystemContext);
  if (!context) {
    return { reducedMotion: false, density: "comfortable" as const };
  }
  return context;
}
