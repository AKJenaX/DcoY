import { SlidersHorizontal } from "lucide-react";
import { Button } from "./button";
import { Badge } from "./badge";
import { cn } from "../utils";

export function FilterBar({
  children,
  activeCount = 0,
  onReset,
  className
}: {
  children: React.ReactNode;
  activeCount?: number;
  onReset?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap items-center gap-3 rounded-ds-lg border border-white/10 bg-card p-3", className)}>
      <SlidersHorizontal aria-hidden="true" className="h-4 w-4 text-slate-400" />
      {children}
      <div className="ml-auto flex items-center gap-2">
        <Badge>{activeCount} active</Badge>
        {onReset ? (
          <Button variant="ghost" size="sm" onClick={onReset}>
            Reset
          </Button>
        ) : null}
      </div>
    </div>
  );
}

export function Pagination({
  page,
  totalPages,
  onPageChange
}: {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  return (
    <nav aria-label="Pagination" className="flex items-center justify-between gap-3">
      <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
        Previous
      </Button>
      <span className="text-sm text-slate-400">
        Page <span className="font-semibold text-white">{page}</span> of {totalPages}
      </span>
      <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
        Next
      </Button>
    </nav>
  );
}
