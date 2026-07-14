import React, { useEffect, useState, useMemo, useRef } from "react";

interface HexagonData {
  id: string;
  x: number;
  y: number;
  r: number;
  h: number;
  f: number;
  opacity: number;
}

interface HexFieldProps {
  density?: "login" | "sidebar" | "sparse";
  width?: number;
  height?: number;
  opacity?: number;
  animate?: boolean;
}

export const HexField: React.FC<HexFieldProps> = ({
  density = "login",
  width = 1920,
  height = 1080,
  opacity = 1.0,
  animate = true,
}) => {
  const containerRef = useRef<SVGSVGElement | null>(null);
  const [dimensions, setDimensions] = useState({ w: width, h: height });

  // Handle window resizing if default sizes are used
  useEffect(() => {
    if (density === "sidebar") {
      setDimensions({ w: 256, h: 1080 });
      return;
    }

    const updateSize = () => {
      if (containerRef.current) {
        setDimensions({
          w: window.innerWidth,
          h: window.innerHeight,
        });
      }
    };

    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, [density]);

  const hexagons = useMemo(() => {
    const hexList: HexagonData[] = [];
    const w = dimensions.w;
    const h = dimensions.h;

    // Config parameters depending on density
    let r = 38;
    let f = 0.58;
    let hMin = 10;
    let hMax = 28;
    
    if (density === "sidebar") {
      r = 20;
      f = 0.6;
      hMin = 0; // Flat
      hMax = 0;
    } else if (density === "sparse") {
      r = 45;
      f = 0.58;
      hMin = 6;
      hMax = 15;
    }

    const colWidth = Math.sqrt(3) * r;
    const rowHeight = 1.5 * r * f;
    const cols = Math.ceil(w / colWidth) + 2;
    const rows = Math.ceil(h / rowHeight) + 2;

    let idCounter = 0;

    for (let row = -2; row < rows; row++) {
      for (let col = -2; col < cols; col++) {
        let x = col * colWidth;
        if (row % 2 !== 0) {
          x += colWidth / 2;
        }
        let y = row * rowHeight;

        // Position jitter
        x += (Math.random() - 0.5) * (density === "sidebar" ? 2 : 4);
        y += (Math.random() - 0.5) * (density === "sidebar" ? 2 : 4);

        // Density gradient probability mapping
        const tx = x / w;
        let prob = 0.5;

        if (density === "login") {
          // Dense on left, thin on right
          if (tx < 0.25) {
            prob = 0.88;
          } else if (tx < 0.6) {
            prob = 0.88 - ((tx - 0.25) / 0.35) * 0.73;
          } else if (tx < 0.85) {
            prob = 0.15 - ((tx - 0.6) / 0.25) * 0.13;
          } else {
            prob = 0.02;
          }
        } else if (density === "sidebar") {
          // Extremely sparse, even distribution
          prob = 0.15;
        } else {
          // Sparse
          prob = 0.25;
        }

        if (Math.random() > prob) continue;

        // Heights
        const heightFactor = 1 - tx;
        const hexHeight = hMin + Math.random() * (hMax - hMin) * (0.3 + 0.7 * heightFactor);
        const cellOpacity = density === "sidebar" ? 0.05 + Math.random() * 0.08 : 1.0;

        hexList.push({
          id: `hex-${density}-${idCounter++}`,
          x,
          y,
          r,
          h: hexHeight,
          f,
          opacity: cellOpacity,
        });
      }
    }

    // Sort Y back-to-front (Painter's Algorithm)
    return hexList.sort((a, b) => a.y - b.y);
  }, [dimensions, density]);

  return (
    <svg
      ref={containerRef}
      viewBox={`0 0 ${dimensions.w} ${dimensions.h}`}
      className="absolute inset-0 w-full h-full pointer-events-none select-none overflow-hidden"
      style={{ opacity, zIndex: 1 }}
      preserveAspectRatio="none"
    >
      <defs>
        {/* Extruded top gradient */}
        <linearGradient id="hex-top-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#1e1e24" />
          <stop offset="100%" stopColor="#0f0f12" />
        </linearGradient>

        {/* Side panels gradients */}
        <linearGradient id="hex-side-l-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#15151b" />
          <stop offset="100%" stopColor="#08080a" />
        </linearGradient>

        <linearGradient id="hex-side-r-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#0f0f13" />
          <stop offset="100%" stopColor="#040405" />
        </linearGradient>
      </defs>

      <g className={animate && density !== "sidebar" ? "animate-pulse-slow" : ""}>
        {hexagons.map((hex) => {
          const { x, y, r, h, f } = hex;
          const dx = (r * Math.sqrt(3)) / 2;
          const dy = (r * f) / 2;
          const ry = r * f;

          // Top face points
          const p0 = { x: x, y: y - ry };
          const p1 = { x: x + dx, y: y - dy };
          const p2 = { x: x + dx, y: y + dy };
          const p3 = { x: x, y: y + ry };
          const p4 = { x: x - dx, y: y + dy };
          const p5 = { x: x - dx, y: y - dy };

          const topPath = `M ${p5.x},${p5.y} L ${p0.x},${p0.y} L ${p1.x},${p1.y} L ${p2.x},${p2.y} L ${p3.x},${p3.y} L ${p4.x},${p4.y} Z`;

          // If flat (height is 0, like in sidebar)
          if (h <= 0) {
            return (
              <polygon
                key={hex.id}
                points={`${p0.x},${p0.y} ${p1.x},${p1.y} ${p2.x},${p2.y} ${p3.x},${p3.y} ${p4.x},${p4.y} ${p5.x},${p5.y}`}
                fill="none"
                stroke="rgba(255, 255, 255, 0.015)"
                strokeWidth="1.2"
                style={{ opacity: hex.opacity }}
              />
            );
          }

          // Extruded side vertices (only 2 panels are visible)
          const p2_b = { x: p2.x, y: p2.y + h };
          const p3_b = { x: p3.x, y: p3.y + h };
          const p4_b = { x: p4.x, y: p4.y + h };

          const sideLeftPath = `M ${p4.x},${p4.y} L ${p3.x},${p3.y} L ${p3_b.x},${p3_b.y} L ${p4_b.x},${p4_b.y} Z`;
          const sideRightPath = `M ${p3.x},${p3.y} L ${p2.x},${p2.y} L ${p2_b.x},${p2_b.y} L ${p3_b.x},${p3_b.y} Z`;

          return (
            <g key={hex.id} className="transition-opacity duration-300" style={{ opacity: hex.opacity }}>
              {/* Left Side Bevel */}
              <path d={sideLeftPath} fill="url(#hex-side-l-grad)" stroke="#1a1a20" strokeWidth="0.5" />
              {/* Right Side Bevel */}
              <path d={sideRightPath} fill="url(#hex-side-r-grad)" stroke="#141418" strokeWidth="0.5" />
              {/* Top Face */}
              <path d={topPath} fill="url(#hex-top-grad)" stroke="rgba(255,255,255,0.05)" strokeWidth="0.8" />
              {/* Top Highlight Rim */}
              <polygon points={`${p5.x},${p5.y} ${p0.x},${p0.y} ${p1.x},${p1.y} ${x},${y}`} fill="rgba(255,255,255,0.02)" stroke="none" />
            </g>
          );
        })}
      </g>
    </svg>
  );
};
export default HexField;
