import React from "react";

interface NavHexagonProps {
  active?: boolean;
  color?: "cyan" | "amber" | "violet";
  size?: number;
  className?: string;
  children?: React.ReactNode;
}

export const NavHexagon: React.FC<NavHexagonProps> = ({
  active = false,
  color = "cyan",
  size = 30,
  className = "",
  children,
}) => {
  // Theme color maps
  const colorMap = {
    cyan: {
      activeStroke: "#00e5ff",
      hoverStroke: "rgba(0, 229, 255, 0.75)",
      idleStroke: "rgba(0, 229, 255, 0.2)",
      activeFill: "rgba(0, 229, 255, 0.12)",
      hoverFill: "rgba(0, 229, 255, 0.04)",
      filter: "drop-shadow(0 0 6px rgba(0, 229, 255, 0.4))",
    },
    amber: {
      activeStroke: "#f5a623",
      hoverStroke: "rgba(245, 166, 35, 0.75)",
      idleStroke: "rgba(245, 166, 35, 0.2)",
      activeFill: "rgba(245, 166, 35, 0.12)",
      hoverFill: "rgba(245, 166, 35, 0.04)",
      filter: "drop-shadow(0 0 6px rgba(245, 166, 35, 0.4))",
    },
    violet: {
      activeStroke: "#a78bfa",
      hoverStroke: "rgba(167, 139, 250, 0.75)",
      idleStroke: "rgba(167, 139, 250, 0.2)",
      activeFill: "rgba(167, 139, 250, 0.12)",
      hoverFill: "rgba(167, 139, 250, 0.04)",
      filter: "drop-shadow(0 0 6px rgba(167, 139, 250, 0.4))",
    },
  };

  const theme = colorMap[color];

  // Dynamic values depending on active state
  const stroke = active ? theme.activeStroke : theme.idleStroke;
  const fill = active ? theme.activeFill : "rgba(255, 255, 255, 0.02)";
  const filter = active ? theme.filter : "none";

  return (
    <div
      className={`relative inline-flex items-center justify-center select-none transition-transform duration-300 transform-style-3d group-hover:-translate-y-0.5 group-hover:scale-105 ${
        active ? "animate-pulse-slow" : ""
      } ${className}`}
      style={{
        width: size,
        height: size * 1.15,
      }}
    >
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 100 115"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Extruded Side Face / Shadow Face behind the main face */}
        <polygon
          points="50,8.5 92.5,32.5 92.5,87.5 50,112.5 7.5,87.5 7.5,32.5"
          fill="#050b14"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="2"
          transform="translate(3, 4)"
          className="transition-transform duration-300 group-hover:translate-x-[4px] group-hover:translate-y-[5px]"
        />

        {/* Main Base Face */}
        <polygon
          points="50,2.5 97.5,30 97.5,85 50,112.5 2.5,85 2.5,30"
          fill={fill}
          stroke={stroke}
          strokeWidth="3.5"
          style={{
            filter,
            transition: "all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)",
          }}
          className="group-hover:stroke-[var(--hover-stroke)] group-hover:fill-[var(--hover-fill)]"
          // CSS variables for group-hover classes
          {...{
            style: {
              "--hover-stroke": theme.hoverStroke,
              "--hover-fill": theme.hoverFill,
              filter,
              fill,
              stroke,
            } as React.CSSProperties,
          }}
        />

        {/* Top Highlight Rim (light reflecting on top face edge) */}
        <polygon
          points="50,2.5 97.5,30 50,47 2.5,30"
          fill="rgba(255,255,255,0.05)"
          stroke="none"
        />
      </svg>

      {/* Center Icon */}
      <div
        className={`relative z-10 flex items-center justify-center transition-all duration-300 ${
          active
            ? "text-white"
            : "text-gray-400 group-hover:text-white"
        }`}
        style={{
          width: size * 0.55,
          height: size * 0.55,
        }}
      >
        {children}
      </div>
    </div>
  );
};
