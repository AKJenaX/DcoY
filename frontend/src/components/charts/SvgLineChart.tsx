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
  height = 140,
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const paddingLeft = 35;
  const paddingRight = 15;
  const paddingTop = 15;
  const paddingBottom = 25;
  const width = 300;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const maxVal = Math.max(...data, 1);
  const minVal = 0;
  const range = maxVal - minVal;

  // Grid lines
  const gridLines = [0, 0.25, 0.5, 0.75, 1];

  // Calculate coordinates for points
  const points = data.map((val, idx) => {
    const x = paddingLeft + (idx / Math.max(1, data.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - ((val - minVal) / range) * chartHeight;
    return { x, y, value: val, label: labels[idx] || "" };
  });

  // Build SVG path strings
  let linePath = "";
  let areaPath = "";

  if (points.length > 0) {
    linePath = `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(" ");
    areaPath = `${linePath} L ${points[points.length - 1].x} ${height - paddingBottom} L ${points[0].x} ${height - paddingBottom} Z`;
  }

  // Generate unique IDs for gradients to avoid overlap issues
  const gradId = `areaGrad-${color.replace("#", "")}`;

  return (
    <div className="relative w-full select-none">
      <svg 
        viewBox={`0 0 ${width} ${height}`} 
        className="w-full h-auto overflow-visible"
      >
        <defs>
          {/* Neon Glow Drop Shadow */}
          <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Area Fill Gradient */}
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.25" />
            <stop offset="100%" stopColor={color} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal Gridlines */}
        {gridLines.map((ratio, idx) => {
          const y = paddingTop + chartHeight * (1 - ratio);
          const gridVal = Math.round(maxVal * ratio);
          return (
            <g key={idx}>
              <line 
                x1={paddingLeft} 
                y1={y} 
                x2={width - paddingRight} 
                y2={y} 
                className="stroke-gray-800/40" 
                strokeWidth="1" 
                strokeDasharray="2,3"
              />
              <text 
                x={paddingLeft - 6} 
                y={y + 3} 
                textAnchor="end" 
                className="fill-gray-500 font-mono text-[8px] font-bold"
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

        {/* Trend Line */}
        {linePath && (
          <path 
            d={linePath} 
            fill="none" 
            stroke={color} 
            strokeWidth="2" 
            className="transition-all duration-300"
            filter="url(#neonGlow)"
          />
        )}

        {/* Interaction points and vertical guidelines */}
        {points.map((p, idx) => {
          const isHovered = hoveredIdx === idx;
          
          return (
            <g key={idx} className="cursor-pointer">
              {/* Invisible vertical sweep area for easy hovering */}
              <rect
                x={p.x - 10}
                y={paddingTop}
                width={20}
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
                  className="stroke-cyan-500/50" 
                  strokeWidth="0.8" 
                  strokeDasharray="1,2"
                />
              )}

              {/* Data Node Point */}
              <circle
                cx={p.x}
                cy={p.y}
                r={isHovered ? 4 : 2}
                fill="#0a0f18"
                stroke={color}
                strokeWidth={isHovered ? 2.5 : 1.5}
                className="transition-all duration-150"
              />

              {/* X Axis Labels (every 2nd or 3rd to avoid overlap) */}
              {(idx === 0 || idx === points.length - 1 || idx === Math.floor(points.length / 2)) && (
                <text 
                  x={p.x} 
                  y={height - paddingBottom + 12} 
                  textAnchor="middle" 
                  className="fill-gray-400 font-mono text-[7.5px] uppercase"
                >
                  {p.label}
                </text>
              )}

              {/* Hover Value Tooltip Overlay */}
              {isHovered && (
                <g>
                  <rect 
                    x={Math.max(10, Math.min(width - 90, p.x - 40))} 
                    y={p.y - 18} 
                    width="80" 
                    height="14" 
                    rx="2"
                    className="fill-[#080d16] stroke-cyan-500/30"
                    strokeWidth="0.5"
                  />
                  <text 
                    x={Math.max(10, Math.min(width - 90, p.x - 40)) + 40} 
                    y={p.y - 8} 
                    textAnchor="middle" 
                    className="fill-cyan-400 font-mono text-[7px] font-bold"
                  >
                    {p.label}: {p.value.toFixed(1)}
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
          className="stroke-gray-800" 
          strokeWidth="1.5"
        />
        <line 
          x1={paddingLeft} 
          y1={paddingTop} 
          x2={paddingLeft} 
          y2={height - paddingBottom} 
          className="stroke-gray-800" 
          strokeWidth="1.5"
        />
      </svg>
    </div>
  );
};
