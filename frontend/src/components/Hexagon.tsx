import React from "react";

interface HexagonProps {
  size?: number;
  className?: string;
  glowColor?: "amber" | "cyan" | "red" | "green" | "none";
  pulse?: boolean;
  onClick?: () => void;
  children?: React.ReactNode;
}

export const Hexagon: React.FC<HexagonProps> = ({
  size = 120,
  className = "",
  glowColor = "none",
  pulse = false,
  onClick,
  children,
}) => {
  const getGlowStyles = () => {
    switch (glowColor) {
      case "amber":
        return {
          stroke: "rgba(245, 166, 35, 0.45)",
          filter: "drop-shadow(0 0 3px rgba(245, 166, 35, 0.2))",
        };
      case "cyan":
        return {
          stroke: "rgba(0, 229, 255, 0.45)",
          filter: "drop-shadow(0 0 3px rgba(0, 229, 255, 0.2))",
        };
      case "red":
        return {
          stroke: "#ef4444",
          filter: "drop-shadow(0 0 10px rgba(239, 68, 68, 0.8))",
        };
      case "green":
        return {
          stroke: "rgba(16, 185, 129, 0.45)",
          filter: "drop-shadow(0 0 3px rgba(16, 185, 129, 0.2))",
        };
      default:
        return {
          stroke: "rgba(255, 255, 255, 0.12)",
        };
    }
  };

  const glowStyles = getGlowStyles();

  return (
    <div
      onClick={onClick}
      className={`relative inline-flex items-center justify-center select-none ${
        onClick ? "cursor-pointer" : ""
      } ${className}`}
      style={{ width: size, height: size * 1.15 }}
    >
      {/* SVG hexagon base */}
      <svg
        className={`absolute inset-0 w-full h-full ${pulse ? "animate-pulse" : ""}`}
        viewBox="0 0 100 115"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <polygon
          className="hex-depth-face"
          points="50,7.5 92.5,32.5 92.5,87.5 50,112.5 7.5,87.5 7.5,32.5"
          fill="#050b14"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="2"
          transform="translate(3 4)"
        />
        <polygon
          className="hex-facet-face"
          points="50,2.5 97.5,30 97.5,85 50,112.5 2.5,85 2.5,30"
          fill="rgba(255,255,255,0.025)"
          stroke="none"
        />
        <polygon
          points="50,2.5 97.5,30 97.5,85 50,112.5 2.5,85 2.5,30"
          fill="#111827"
          strokeWidth="3.5"
          style={glowStyles}
        />
        <polygon
          className="hex-facet-highlight"
          points="50,2.5 97.5,30 50,47 2.5,30"
          fill="rgba(255,255,255,0.055)"
          stroke="none"
        />
      </svg>

      {/* Hexagon internal content container */}
      <div className="relative z-10 p-4 flex flex-col items-center justify-center text-center w-full h-full text-white">
        {children}
      </div>
    </div>
  );
};
