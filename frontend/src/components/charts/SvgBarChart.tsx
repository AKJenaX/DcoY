import React, { useState } from "react";

interface BarChartProps {
  data: Array<{ label: string; value: number }>;
  color?: string;
  height?: number;
}

export const SvgBarChart: React.FC<BarChartProps> = ({
  data,
  color = "#22d3ee", // cyan-400
  height = 140,
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Constants for layout
  const paddingLeft = 35;
  const paddingRight = 10;
  const paddingTop = 15;
  const paddingBottom = 25;
  const width = 300;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  // Find max value for scaling
  const maxVal = Math.max(...data.map(d => d.value), 1);

  // Grid lines
  const gridLines = [0, 0.25, 0.5, 0.75, 1];

  return (
    <div className="relative w-full select-none">
      <svg 
        viewBox={`0 0 ${width} ${height}`} 
        className="w-full h-auto overflow-visible"
      >
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

        {/* Bars */}
        {data.map((item, idx) => {
          const barCount = data.length;
          const barSpacing = chartWidth / barCount;
          const barWidth = Math.max(4, barSpacing * 0.6);
          const x = paddingLeft + (idx * barSpacing) + (barSpacing - barWidth) / 2;
          
          const barHeight = (item.value / maxVal) * chartHeight;
          const y = paddingTop + chartHeight - barHeight;

          const isHovered = hoveredIdx === idx;

          return (
            <g 
              key={idx}
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
              className="cursor-pointer"
            >
              {/* Highlight background bar on hover */}
              {isHovered && (
                <rect 
                  x={x - (barSpacing - barWidth) / 4} 
                  y={paddingTop} 
                  width={barWidth + (barSpacing - barWidth) / 2} 
                  height={chartHeight} 
                  className="fill-cyan-500/5 stroke-none"
                />
              )}

              {/* Data Bar */}
              <rect 
                x={x} 
                y={y} 
                width={barWidth} 
                height={Math.max(1, barHeight)} 
                fill={color} 
                className="transition-all duration-300 opacity-80 hover:opacity-100"
                style={{
                  filter: isHovered ? "drop-shadow(0 0 6px rgba(34,211,238,0.4))" : "none"
                }}
              />

              {/* X Axis Label */}
              <text 
                x={x + barWidth / 2} 
                y={height - paddingBottom + 12} 
                textAnchor="middle" 
                className="fill-gray-400 font-mono text-[7.5px] uppercase truncate"
                style={{ maxWidth: barSpacing }}
              >
                {item.label.length > 8 ? `${item.label.slice(0, 6)}..` : item.label}
              </text>

              {/* Tooltip detail over active bar */}
              {isHovered && (
                <g>
                  {/* Tooltip Box */}
                  <rect 
                    x={Math.max(10, Math.min(width - 90, x - 40))} 
                    y={y - 18} 
                    width="80" 
                    height="14" 
                    rx="2"
                    className="fill-[#080d16] stroke-cyan-500/30"
                    strokeWidth="0.5"
                  />
                  <text 
                    x={Math.max(10, Math.min(width - 90, x - 40)) + 40} 
                    y={y - 8} 
                    textAnchor="middle" 
                    className="fill-cyan-400 font-mono text-[7px] font-bold"
                  >
                    {item.label}: {item.value}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* X and Y baseline axes */}
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
