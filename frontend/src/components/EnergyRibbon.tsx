import React, { useMemo } from "react";

interface Point {
  x: number;
  y: number;
}

interface EnergyRibbonProps {
  mode?: "login" | "map";
  customPointsA?: Point[];
  customPointsB?: Point[];
  width?: number;
  height?: number;
  opacity?: number;
  animate?: boolean;
  raw?: boolean;
}

export const EnergyRibbon: React.FC<EnergyRibbonProps> = ({
  mode = "login",
  customPointsA,
  customPointsB,
  width = 1920,
  height = 1080,
  opacity = 0.9,
  animate = true,
  raw = false,
}) => {
  // Helper to generate cubic bezier control points for smooth natural curves
  const generateBezierPath = (points: Point[], scaleMode: "login" | "map") => {
    if (points.length === 0) return "";
    if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
    
    let d = `M ${points[0].x} ${points[0].y}`;
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i];
      const p1 = points[i + 1];
      
      const dx = p1.x - p0.x;
      const dy = p1.y - p0.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      // Stable coordinate hash between 0.1 and 0.9 to ensure deterministic curves
      const hash = 0.1 + (Math.abs(Math.sin(p0.x * 12.9898 + p0.y * 78.233) * 43758.5453) % 0.8);
      
      // Control point tension (0.2 to 0.45)
      const tension = 0.2 + hash * 0.25;
      
      // Perpendicular offsets to create organic dodging/obstacle avoidance effect
      const perpX = -dy / (dist || 1);
      const perpY = dx / (dist || 1);
      
      // Organic curve tightness variations (amplitude of control point offset)
      // Map mode has tighter nodes so we scale displacement accordingly
      const amplitudeFactor = scaleMode === "map" ? 0.22 : 0.35;
      const curveTightness = (hash - 0.5) * dist * amplitudeFactor;
      
      const cp1x = p0.x + dx * tension + perpX * curveTightness;
      const cp1y = p0.y + dy * tension + perpY * curveTightness;
      
      const cp2x = p1.x - dx * tension - perpX * curveTightness;
      const cp2y = p1.y - dy * tension - perpY * curveTightness;
      
      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p1.x} ${p1.y}`;
    }
    return d;
  };

  // 1. Coordinates for Login Mode
  const pointsA = useMemo(() => {
    return customPointsA || [
      { x: -50, y: 350 },
      { x: 280, y: 560 },
      { x: 620, y: 220 },
      { x: 960, y: 720 },
      { x: 1300, y: 380 },
      { x: 1650, y: 640 },
      { x: 1980, y: 440 }
    ];
  }, [customPointsA]);

  const pointsB = useMemo(() => {
    return customPointsB || [
      { x: -50, y: 650 },
      { x: 280, y: 280 },
      { x: 620, y: 620 },
      { x: 960, y: 300 },
      { x: 1300, y: 660 },
      { x: 1650, y: 360 },
      { x: 1980, y: 560 }
    ];
  }, [customPointsB]);

  // Generate SVG path geometries
  const pathA = useMemo(() => generateBezierPath(pointsA, mode), [pointsA, mode]);
  const pathB = useMemo(() => generateBezierPath(pointsB, mode), [pointsB, mode]);

  // Identify waypoints along both lines (e.g. 2nd and 5th points)
  const waypointsA = useMemo(() => {
    if (pointsA.length <= 2) return [];
    return pointsA.slice(1, -1); // Intermediaries are intermediate nodes on the Dijkstra path
  }, [pointsA]);

  const waypointsB = useMemo(() => {
    if (pointsB.length <= 2) return [];
    return pointsB.slice(1, -1);
  }, [pointsB]);

  // Small hexagon path generator
  const getHexPath = (x: number, y: number, r = 8) => {
    const f = 0.85; // flattening factor
    const dx = (r * Math.sqrt(3)) / 2;
    const dy = (r * f) / 2;
    const ry = r * f;
    return `M ${x},${y - ry} L ${x + dx},${y - dy} L ${x + dx},${y + dy} L ${x},${y + ry} L ${x - dx},${y + dy} L ${x - dx},${y - dy} Z`;
  };

  const content = (
    <>
      <defs>
        {/* Glow Filters */}
        <filter id="glow-amber-ribbon" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8" result="blur1" />
          <feGaussianBlur stdDeviation="22" result="blur2" />
          <feMerge>
            <feMergeNode in="blur2" />
            <feMergeNode in="blur1" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        <filter id="glow-cyan-ribbon" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8" result="blur1" />
          <feGaussianBlur stdDeviation="22" result="blur2" />
          <feMerge>
            <feMergeNode in="blur2" />
            <feMergeNode in="blur1" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        <filter id="glow-violet-ribbon" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8" result="blur1" />
          <feGaussianBlur stdDeviation="22" result="blur2" />
          <feMerge>
            <feMergeNode in="blur2" />
            <feMergeNode in="blur1" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        <filter id="ribbon-mask-blur">
          <feGaussianBlur stdDeviation="12" />
        </filter>

        {/* Intersection mask: Violet glow is ONLY visible where Amber intersects Cyan's envelope */}
        <mask id="cyan-ribbon-mask">
          <rect x="-100" y="-100" width={width + 200} height={height + 200} fill="black" />
          {/* Cyan glow region in mask */}
          <path d={pathB} fill="none" stroke="white" strokeWidth="36" filter="url(#ribbon-mask-blur)" opacity="0.8" />
          {/* Cyan core region in mask */}
          <path d={pathB} fill="none" stroke="white" strokeWidth="10" />
        </mask>
      </defs>

      {/* Amber Path */}
      {pathA && (
        <g className={animate ? "animate-pulse-slow" : ""}>
          <path d={pathA} fill="none" stroke="#ffb300" strokeWidth="16" filter="url(#glow-amber-ribbon)" opacity="0.3" />
          <path d={pathA} fill="none" stroke="#ffd54f" strokeWidth="4.5" />
        </g>
      )}

      {/* Cyan Path */}
      {pathB && (
        <g className={animate ? "animate-pulse-slow" : ""}>
          <path d={pathB} fill="none" stroke="#00e5ff" strokeWidth="16" filter="url(#glow-cyan-ribbon)" opacity="0.3" />
          <path d={pathB} fill="none" stroke="#80deea" strokeWidth="4.5" />
        </g>
      )}

      {/* Violet Intersection Path (only rendered where Amber and Cyan overlap) */}
      {pathA && pathB && (
        <g>
          <path
            d={pathA}
            fill="none"
            stroke="#d500f9"
            strokeWidth="18"
            filter="url(#glow-violet-ribbon)"
            opacity="0.65"
            mask="url(#cyan-ribbon-mask)"
          />
          <path
            d={pathA}
            fill="none"
            stroke="#f48fb1"
            strokeWidth="4.5"
            mask="url(#cyan-ribbon-mask)"
          />
        </g>
      )}

      {/* Waypoint Markers - Amber Path */}
      {waypointsA.map((pt, idx) => (
        <g key={`waypoint-a-${idx}`} className={animate ? "animate-pulse" : ""}>
          <path d={getHexPath(pt.x, pt.y, 8)} fill="rgba(8, 8, 12, 0.9)" stroke="#ffd54f" strokeWidth="1.5" />
          <circle cx={pt.x} cy={pt.y} r="2" fill="#ffd54f" />
        </g>
      ))}

      {/* Waypoint Markers - Cyan Path */}
      {waypointsB.map((pt, idx) => (
        <g key={`waypoint-b-${idx}`} className={animate ? "animate-pulse" : ""}>
          <path d={getHexPath(pt.x, pt.y, 8)} fill="rgba(8, 8, 12, 0.9)" stroke="#80deea" strokeWidth="1.5" />
          <circle cx={pt.x} cy={pt.y} r="2" fill="#80deea" />
        </g>
      ))}
    </>
  );

  if (raw) {
    return content;
  }

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="absolute inset-0 w-full h-full pointer-events-none select-none overflow-hidden"
      style={{ opacity, zIndex: 2 }}
      preserveAspectRatio="none"
    >
      {content}
    </svg>
  );
};
export default EnergyRibbon;
