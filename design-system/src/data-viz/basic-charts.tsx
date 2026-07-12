import { chartTheme } from "./chart-theme";
import { cn } from "../utils";

export type XYPoint = { label: string; value: number };

function normalize(points: XYPoint[]) {
  const max = Math.max(1, ...points.map((point) => point.value));
  return points.map((point, index) => ({
    ...point,
    x: points.length === 1 ? 50 : (index / (points.length - 1)) * 100,
    y: 100 - (point.value / max) * 80 - 10
  }));
}

export function LineChart({ data, className }: { data: XYPoint[]; className?: string }) {
  const points = normalize(data);
  const path = points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x},${point.y}`).join(" ");
  return (
    <svg role="img" aria-label="Line chart" viewBox="0 0 100 100" className={cn("h-full w-full overflow-visible", className)} preserveAspectRatio="none">
      <path d={path} fill="none" stroke={chartTheme.colors.primary} strokeWidth="2" vectorEffect="non-scaling-stroke" />
      {points.map((point) => <circle key={point.label} cx={point.x} cy={point.y} r="1.6" fill={chartTheme.colors.accent} />)}
    </svg>
  );
}

export function AreaChart({ data, className }: { data: XYPoint[]; className?: string }) {
  const points = normalize(data);
  const line = points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x},${point.y}`).join(" ");
  const area = `${line} L100,100 L0,100 Z`;
  return (
    <svg role="img" aria-label="Area chart" viewBox="0 0 100 100" className={cn("h-full w-full", className)} preserveAspectRatio="none">
      <defs>
        <linearGradient id="dcoy-area-gradient" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={chartTheme.colors.primary} stopOpacity="0.35" />
          <stop offset="100%" stopColor={chartTheme.colors.primary} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#dcoy-area-gradient)" />
      <path d={line} fill="none" stroke={chartTheme.colors.primary} strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

export function BarChart({ data, className }: { data: XYPoint[]; className?: string }) {
  const max = Math.max(1, ...data.map((point) => point.value));
  const width = 100 / Math.max(1, data.length);
  return (
    <svg role="img" aria-label="Bar chart" viewBox="0 0 100 100" className={cn("h-full w-full", className)} preserveAspectRatio="none">
      {data.map((point, index) => {
        const height = (point.value / max) * 82;
        return <rect key={point.label} x={index * width + width * 0.18} y={92 - height} width={width * 0.64} height={height} rx="1.5" fill={chartTheme.colors.primary} opacity="0.9" />;
      })}
    </svg>
  );
}

export function DonutChart({ data, className }: { data: XYPoint[]; className?: string }) {
  const total = data.reduce((sum, point) => sum + point.value, 0) || 1;
  let offset = 25;
  const palette = [chartTheme.colors.primary, chartTheme.colors.secondary, chartTheme.colors.accent, chartTheme.colors.success, chartTheme.colors.warning, chartTheme.colors.danger];
  return (
    <svg role="img" aria-label="Donut chart" viewBox="0 0 42 42" className={cn("h-full w-full", className)}>
      <circle cx="21" cy="21" r="15.915" fill="transparent" stroke={chartTheme.colors.grid} strokeWidth="4" />
      {data.map((point, index) => {
        const percent = (point.value / total) * 100;
        const current = offset;
        offset -= percent;
        return <circle key={point.label} cx="21" cy="21" r="15.915" fill="transparent" stroke={palette[index % palette.length]} strokeWidth="4" strokeDasharray={`${percent} ${100 - percent}`} strokeDashoffset={current} />;
      })}
    </svg>
  );
}

export function RadarChart({ data, className }: { data: XYPoint[]; className?: string }) {
  const max = Math.max(1, ...data.map((point) => point.value));
  const center = 50;
  const radius = 38;
  const points = data.map((point, index) => {
    const angle = (Math.PI * 2 * index) / data.length - Math.PI / 2;
    const valueRadius = (point.value / max) * radius;
    return `${center + Math.cos(angle) * valueRadius},${center + Math.sin(angle) * valueRadius}`;
  });
  return (
    <svg role="img" aria-label="Radar chart" viewBox="0 0 100 100" className={cn("h-full w-full", className)}>
      <polygon points={points.join(" ")} fill={chartTheme.colors.primary} fillOpacity="0.22" stroke={chartTheme.colors.primary} strokeWidth="1.5" />
    </svg>
  );
}

export function Heatmap({ data, className }: { data: number[][]; className?: string }) {
  const rows = data.length;
  const cols = Math.max(1, ...data.map((row) => row.length));
  const max = Math.max(1, ...data.flat());
  return (
    <div role="img" aria-label="Heatmap" className={cn("grid h-full w-full gap-1", className)} style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
      {data.flatMap((row, rowIndex) =>
        row.map((value, colIndex) => <span key={`${rowIndex}-${colIndex}`} className="rounded-[3px] bg-primary" style={{ opacity: 0.12 + (value / max) * 0.78 }} />)
      )}
    </div>
  );
}
