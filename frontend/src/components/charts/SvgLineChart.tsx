import React, { useState } from "react";

interface LineChartProps {
  data: number[];
  labels: string[];
  color?: string;
  height?: number;
}

export const SvgLineChart: React.FC<LineChartProps> = ({
  data,
  labels,
  color = "#22d3ee", // cyan-400
  height = 180,
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const paddingLeft = 44;
  const paddingRight = 20;
  const paddingTop = 18;
  const paddingBottom = 30;
  const width = 600;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const maxVal = Math.max(...data, 1);
  const niceMax = Math.ceil(maxVal / 5) * 5; // Round up to nearest 5
  const minVal = 0;
  const range = niceMax - minVal;

  // Grid lines — 5 evenly spaced
  const gridCount = 5;
  const gridLines = Array.from({ length: gridCount + 1 }, (_, i) => i / gridCount);

  // Calculate coordinates for points
  const points = data.map((val, idx) => {
    const x = paddingLeft + (idx / Math.max(1, data.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - ((val - minVal) / range) * chartHeight;
    return { x, y, value: val, label: labels[idx] || "" };
  });

  // Build SVG path strings — smooth curves using cardinal spline
  let linePath = "";
  let areaPath = "";

  if (points.length > 1) {
    // Catmull-Rom to cubic bezier for smooth curves
    const tension = 0.3;
    let d = `M ${points[0].x} ${points[0].y}`;

    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[Math.max(0, i - 1)];
      const p1 = points[i];
      const p2 = points[i + 1];
      const p3 = points[Math.min(points.length - 1, i + 2)];

      const cp1x = p1.x + (p2.x - p0.x) * tension;
      const cp1y = p1.y + (p2.y - p0.y) * tension;
      const cp2x = p2.x - (p3.x - p1.x) * tension;
      const cp2y = p2.y - (p3.y - p1.y) * tension;

      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
    }

    linePath = d;
    areaPath = `${d} L ${points[points.length - 1].x} ${height - paddingBottom} L ${points[0].x} ${height - paddingBottom} Z`;
  } else if (points.length === 1) {
    linePath = `M ${points[0].x} ${points[0].y}`;
  }

  // Generate unique IDs for gradients
  const gradId = `areaGrad-${color.replace("#", "")}`;
  const glowId = `neonGlow-${color.replace("#", "")}`;

  // Determine which X-axis labels to show (max ~8 labels to avoid overlap)
  const maxXLabels = 8;
  const labelInterval = Math.max(1, Math.ceil(data.length / maxXLabels));

  return (
    <div className="relative w-full select-none">
      <svg 
        viewBox={`0 0 ${width} ${height}`} 
        className="w-full h-auto"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          {/* Neon Glow Filter */}
          <filter id={glowId} x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Area Fill Gradient */}
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.2" />
            <stop offset="100%" stopColor={color} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal Gridlines + Y-axis labels */}
        {gridLines.map((ratio, idx) => {
          const y = paddingTop + chartHeight * (1 - ratio);
          const gridVal = Math.round(niceMax * ratio);
          return (
            <g key={idx}>
              <line 
                x1={paddingLeft} 
                y1={y} 
                x2={width - paddingRight} 
                y2={y} 
                className="stroke-gray-800/40" 
                strokeWidth="0.8" 
                strokeDasharray="3,4"
              />
              <text 
                x={paddingLeft - 8} 
                y={y + 3.5} 
                textAnchor="end" 
                className="fill-gray-500 font-mono" 
                style={{ fontSize: '9px' }}
              >
                {gridVal}
              </text>
            </g>
          );
        })}

        {/* Shaded Area Under Curve */}
        {areaPath && (
          <path d={areaPath} fill={`url(#${gradId})`} className="stroke-none" />
        )}

        {/* Trend Line — smooth with glow */}
        {linePath && (
          <path 
            d={linePath} 
            fill="none" 
            stroke={color} 
            strokeWidth="2.5" 
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-all duration-300"
            filter={`url(#${glowId})`}
          />
        )}

        {/* Interaction points */}
        {points.map((p, idx) => {
          const isHovered = hoveredIdx === idx;
          
          return (
            <g key={idx} className="cursor-pointer">
              {/* Invisible vertical sweep area for easy hovering */}
              <rect
                x={p.x - (chartWidth / data.length / 2)}
                y={paddingTop}
                width={chartWidth / data.length}
                height={chartHeight}
                fill="transparent"
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              />

              {/* Vertical dotted cursor on hover */}
              {isHovered && (
                <line 
                  x1={p.x} 
                  y1={paddingTop} 
                  x2={p.x} 
                  y2={height - paddingBottom} 
                  stroke={color}
                  strokeOpacity="0.3"
                  strokeWidth="1" 
                  strokeDasharray="2,3"
                />
              )}

              {/* Data Node Point */}
              <circle
                cx={p.x}
                cy={p.y}
                r={isHovered ? 4.5 : 2.5}
                fill={isHovered ? color : "#0a0f18"}
                stroke={color}
                strokeWidth={isHovered ? 2.5 : 1.5}
                className="transition-all duration-150"
              />

              {/* X Axis Labels — evenly spaced to avoid overlap */}
              {(idx % labelInterval === 0 || idx === points.length - 1) && (
                <text 
                  x={p.x} 
                  y={height - paddingBottom + 14} 
                  textAnchor="middle" 
                  className="fill-gray-500 font-mono"
                  style={{ fontSize: '8px' }}
                >
                  {p.label}
                </text>
              )}

              {/* Hover Value Tooltip */}
              {isHovered && (
                <g>
                  <rect 
                    x={Math.max(paddingLeft, Math.min(width - paddingRight - 80, p.x - 40))} 
                    y={p.y - 26} 
                    width="80" 
                    height="18" 
                    rx="3"
                    fill="#080d16"
                    stroke={color}
                    strokeOpacity="0.4"
                    strokeWidth="0.8"
                  />
                  <text 
                    x={Math.max(paddingLeft, Math.min(width - paddingRight - 80, p.x - 40)) + 40} 
                    y={p.y - 14} 
                    textAnchor="middle" 
                    fill={color}
                    className="font-mono font-bold"
                    style={{ fontSize: '9px' }}
                  >
                    {p.value.toFixed(1)} ms
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Baseline Axes */}
        <line 
          x1={paddingLeft} 
          y1={height - paddingBottom} 
          x2={width - paddingRight} 
          y2={height - paddingBottom} 
          className="stroke-gray-700" 
          strokeWidth="1"
        />
        <line 
          x1={paddingLeft} 
          y1={paddingTop} 
          x2={paddingLeft} 
          y2={height - paddingBottom} 
          className="stroke-gray-700" 
          strokeWidth="1"
        />
      </svg>
    </div>
  );
};
