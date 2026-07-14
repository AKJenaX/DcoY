import React, { useState } from "react";

interface DonutChartProps {
  data: Array<{ label: string; value: number }>;
  colors?: string[];
  size?: number;
}

export const SvgDonutChart: React.FC<DonutChartProps> = ({
  data,
  colors = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6"], // red, amber, green, blue, purple
  size = 130,
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const total = data.reduce((sum, d) => sum + d.value, 0) || 1;

  // Circle dimensions
  const r = 38;
  const strokeWidth = 10;
  const center = size / 2;
  const circumference = 2 * Math.PI * r;

  let accumulatedPercent = 0;

  return (
    <div className="relative flex items-center justify-center select-none w-full">
      <svg 
        width={size} 
        height={size} 
        viewBox={`0 0 ${size} ${size}`}
        className="transform -rotate-90 overflow-visible"
      >
        {/* Underlay tracking circle */}
        <circle
          cx={center}
          cy={center}
          r={r}
          fill="none"
          className="stroke-gray-900"
          strokeWidth={strokeWidth}
        />

        {data.map((item, idx) => {
          const percent = item.value / total;
          const strokeLength = percent * circumference;
          const strokeOffset = circumference - (accumulatedPercent * circumference) + (circumference / 4); 
          // Offset by circumference/4 because SVG circles start at 3 o'clock and we rotated -90deg.
          
          accumulatedPercent += percent;

          const color = colors[idx % colors.length];
          const isHovered = hoveredIdx === idx;

          return (
            <circle
              key={idx}
              cx={center}
              cy={center}
              r={r}
              fill="none"
              stroke={color}
              strokeWidth={isHovered ? strokeWidth + 2.5 : strokeWidth}
              strokeDasharray={`${strokeLength} ${circumference}`}
              strokeDashoffset={strokeOffset}
              strokeLinecap="butt"
              className="transition-all duration-200 cursor-pointer"
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{
                filter: isHovered ? `drop-shadow(0 0 4px ${color})` : "none"
              }}
            />
          );
        })}
      </svg>

      {/* Center Label HUD */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center font-mono">
        {hoveredIdx !== null ? (
          <>
            <span className="text-[8px] text-gray-500 uppercase tracking-wider">
              {data[hoveredIdx].label}
            </span>
            <span className="text-sm font-black text-white">
              {data[hoveredIdx].value}
            </span>
            <span className="text-[7.5px] text-cyan-400 font-bold">
              {((data[hoveredIdx].value / total) * 100).toFixed(0)}%
            </span>
          </>
        ) : (
          <>
            <span className="text-[8px] text-gray-500 uppercase tracking-widest">
              Total Count
            </span>
            <span className="text-base font-black text-white">
              {total === 1 && data.reduce((sum, d) => sum + d.value, 0) === 0 ? 0 : total}
            </span>
            <span className="text-[7px] text-gray-500">Breakdown</span>
          </>
        )}
      </div>
    </div>
  );
};
export default SvgDonutChart;
