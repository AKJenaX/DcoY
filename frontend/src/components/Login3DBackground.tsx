import React, { useEffect, useState } from "react";
import { HexField } from "./HexField";
import { EnergyRibbon } from "./EnergyRibbon";

interface Login3DBackgroundProps {
  mode?: "hero" | "ambient";
}

export const Login3DBackground: React.FC<Login3DBackgroundProps> = ({ mode = "hero" }) => {
  const [animate, setAnimate] = useState(true);

  useEffect(() => {
    // 1. Accessibility check for reduced motion
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setAnimate(false);
      return;
    }

    // 2. Visibility observer to pause/disable animations when tab is unfocused
    const handleVisibilityChange = () => {
      setAnimate(!document.hidden);
    };
    
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  return (
    <div className="w-full h-full absolute inset-0 bg-[#030305] overflow-hidden select-none">
      {/* Background Grid Accent Lines */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
          zIndex: 0
        }}
      />

      {/* 3D Hexagon Column Field (Painter's Algorithm Extrusion) */}
      <HexField density={mode === "ambient" ? "sparse" : "login"} animate={animate} opacity={mode === "ambient" ? 0.15 : 0.65} />

      {/* Organic Energy Ribbons (Amber + Cyan + Violet Intersections) */}
      <EnergyRibbon mode={mode === "ambient" ? "ambient" : "login"} animate={animate} opacity={mode === "ambient" ? 0.35 : 0.9} />
    </div>
  );
};
export default Login3DBackground;
