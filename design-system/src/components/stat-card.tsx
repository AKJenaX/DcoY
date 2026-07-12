import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Card } from "./card";
import { Badge } from "./badge";
import { cn } from "../utils";

export type Trend = "up" | "down" | "flat";

export function StatisticCard({
  label,
  value,
  helper,
  trend = "flat",
  trendLabel,
  className
}: {
  label: string;
  value: string | number;
  helper?: string;
  trend?: Trend;
  trendLabel?: string;
  className?: string;
}) {
  const Icon = trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus;
  const tone = trend === "up" ? "success" : trend === "down" ? "danger" : "default";
  return (
    <Card interactive spotlight className={cn("min-h-[148px]", className)}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.04em] text-slate-400">{label}</div>
          <div className="mt-3 text-4xl font-bold leading-none text-white">{value}</div>
          {helper ? <div className="mt-3 text-sm text-slate-400">{helper}</div> : null}
        </div>
        {trendLabel ? (
          <Badge variant={tone} className="gap-1">
            <Icon aria-hidden="true" className="h-3.5 w-3.5" />
            {trendLabel}
          </Badge>
        ) : null}
      </div>
    </Card>
  );
}

export function MetricCard(props: React.ComponentProps<typeof StatisticCard>) {
  return <StatisticCard {...props} />;
}
