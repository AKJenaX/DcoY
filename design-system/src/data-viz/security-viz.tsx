import { Badge } from "../components/badge";
import { cn } from "../utils";
import { chartTheme } from "./chart-theme";

export function MITREMatrix({
  techniques,
  className
}: {
  techniques: Array<{ tactic: string; technique: string; status: "covered" | "partial" | "gap" }>;
  className?: string;
}) {
  const variants = { covered: "success", partial: "warning", gap: "default" } as const;
  return (
    <div className={cn("grid gap-3 md:grid-cols-3 xl:grid-cols-4", className)}>
      {techniques.map((item) => (
        <div key={`${item.tactic}-${item.technique}`} className="min-h-28 rounded-ds border border-white/10 bg-white/[0.025] p-3">
          <div className="text-xs font-semibold uppercase tracking-[0.04em] text-slate-500">{item.tactic}</div>
          <div className="mt-2 text-sm font-semibold text-white">{item.technique}</div>
          <Badge className="mt-3" variant={variants[item.status]}>{item.status}</Badge>
        </div>
      ))}
    </div>
  );
}

export function NetworkGraph({ nodes, links, className }: { nodes: Array<{ id: string; x: number; y: number; critical?: boolean }>; links: Array<{ source: string; target: string }>; className?: string }) {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return (
    <svg role="img" aria-label="Network graph" viewBox="0 0 100 100" className={cn("h-full w-full", className)}>
      {links.map((link) => {
        const source = byId.get(link.source);
        const target = byId.get(link.target);
        if (!source || !target) return null;
        return <line key={`${link.source}-${link.target}`} x1={source.x} y1={source.y} x2={target.x} y2={target.y} stroke={chartTheme.colors.grid} strokeOpacity="0.7" strokeWidth="0.6" />;
      })}
      {nodes.map((node) => <circle key={node.id} cx={node.x} cy={node.y} r={node.critical ? 2.8 : 2} fill={node.critical ? chartTheme.colors.danger : chartTheme.colors.primary} />)}
    </svg>
  );
}

export function ThreatMap({ points, className }: { points: Array<{ x: number; y: number; severity?: "low" | "medium" | "high" }>; className?: string }) {
  return (
    <div role="img" aria-label="Threat map" className={cn("relative h-full w-full rounded-ds bg-surface", className)}>
      {points.map((point, index) => (
        <span
          key={index}
          className={cn("absolute h-2.5 w-2.5 rounded-full shadow-glow", point.severity === "high" ? "bg-danger" : point.severity === "medium" ? "bg-warning" : "bg-primary")}
          style={{ left: `${point.x}%`, top: `${point.y}%` }}
        />
      ))}
    </div>
  );
}

export function TimelineChart({ data, className }: { data: Array<{ label: string; value: number }>; className?: string }) {
  const max = Math.max(1, ...data.map((item) => item.value));
  return (
    <div role="img" aria-label="Timeline chart" className={cn("flex h-full items-end gap-2", className)}>
      {data.map((item) => (
        <div key={item.label} className="flex flex-1 flex-col items-center gap-2">
          <span className="w-full rounded-t-ds bg-accent" style={{ height: `${Math.max(8, (item.value / max) * 100)}%` }} />
          <span className="text-[10px] text-slate-500">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
