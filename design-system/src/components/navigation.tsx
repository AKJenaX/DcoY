import type { LucideIcon } from "lucide-react";
import { ChevronRight, Shield } from "lucide-react";
import { cn } from "../utils";
import { Button } from "./button";
import { SearchBar } from "./input";

export function Topbar({
  product = "DcoY",
  subtitle = "AI Security Operations",
  searchValue = "",
  onSearchChange,
  actions
}: {
  product?: string;
  subtitle?: string;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  actions?: React.ReactNode;
}) {
  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-white/10 bg-background/85 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-ds border border-primary/25 bg-primary/10 text-primary">
          <Shield aria-hidden="true" className="h-5 w-5" />
        </div>
        <div>
          <div className="text-sm font-semibold text-white">{product}</div>
          <div className="text-xs text-slate-400">{subtitle}</div>
        </div>
      </div>
      {onSearchChange ? (
        <div className="hidden w-[min(42vw,520px)] md:block">
          <SearchBar value={searchValue} onChange={onSearchChange} placeholder="Search threats, rules, cases..." />
        </div>
      ) : null}
      <div className="flex items-center gap-2">{actions}</div>
    </header>
  );
}

export function Sidebar({
  items,
  activeId,
  onSelect,
  footer
}: {
  items: Array<{ id: string; label: string; icon?: LucideIcon; badge?: string }>;
  activeId?: string;
  onSelect?: (id: string) => void;
  footer?: React.ReactNode;
}) {
  return (
    <aside className="flex h-dvh w-72 shrink-0 flex-col border-r border-white/10 bg-surface p-4">
      <div className="mb-6 px-2 text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">Operations</div>
      <nav className="flex flex-1 flex-col gap-1" aria-label="Primary navigation">
        {items.map((item) => {
          const Icon = item.icon;
          const active = item.id === activeId;
          return (
            <Button
              key={item.id}
              type="button"
              variant="ghost"
              className={cn("justify-start px-3 text-slate-300", active && "bg-primary/10 text-primary")}
              aria-current={active ? "page" : undefined}
              onClick={() => onSelect?.(item.id)}
            >
              {Icon ? <Icon aria-hidden="true" className="h-4 w-4" /> : null}
              <span className="flex-1 text-left">{item.label}</span>
              {item.badge ? <span className="text-xs text-slate-500">{item.badge}</span> : null}
            </Button>
          );
        })}
      </nav>
      {footer ? <div className="mt-6 border-t border-white/10 pt-4">{footer}</div> : null}
    </aside>
  );
}

export function Breadcrumbs({ items }: { items: Array<{ label: string; href?: string }> }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm text-slate-400">
      {items.map((item, index) => {
        const last = index === items.length - 1;
        return (
          <span key={`${item.label}-${index}`} className="flex items-center gap-2">
            {item.href && !last ? (
              <a href={item.href} className="hover:text-white">
                {item.label}
              </a>
            ) : (
              <span aria-current={last ? "page" : undefined} className={last ? "text-white" : undefined}>
                {item.label}
              </span>
            )}
            {!last ? <ChevronRight aria-hidden="true" className="h-3.5 w-3.5" /> : null}
          </span>
        );
      })}
    </nav>
  );
}
