import { cn } from "../utils";
import { Badge } from "./badge";

export type TimelineItem = {
  id: string;
  title: string;
  timestamp: string;
  description?: string;
  tone?: "default" | "primary" | "success" | "warning" | "danger";
};

export function Timeline({ items, className }: { items: TimelineItem[]; className?: string }) {
  return (
    <ol className={cn("space-y-4", className)}>
      {items.map((item) => (
        <li key={item.id} className="relative border-l border-white/10 pl-5">
          <span className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full bg-primary shadow-glow" aria-hidden="true" />
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="text-sm font-semibold text-white">{item.title}</h4>
            <Badge variant={item.tone === "default" ? "default" : item.tone}>{item.timestamp}</Badge>
          </div>
          {item.description ? <p className="mt-2 text-sm leading-6 text-slate-400">{item.description}</p> : null}
        </li>
      ))}
    </ol>
  );
}

export function ActivityFeed(props: React.ComponentProps<typeof Timeline>) {
  return <Timeline {...props} />;
}
