import type { LucideIcon } from "lucide-react";
import { SearchX } from "lucide-react";
import { Button } from "./button";
import { cn } from "../utils";

export function EmptyState({
  icon: Icon = SearchX,
  title,
  description,
  actionLabel,
  onAction,
  className
}: {
  icon?: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex min-h-[280px] flex-col items-center justify-center rounded-ds-lg border border-dashed border-white/10 p-10 text-center", className)}>
      <div className="mb-5 rounded-ds-lg border border-white/10 bg-white/[0.03] p-4 text-slate-300">
        <Icon aria-hidden="true" className="h-8 w-8" />
      </div>
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      {description ? <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">{description}</p> : null}
      {actionLabel && onAction ? (
        <Button className="mt-6" variant="outline" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}
