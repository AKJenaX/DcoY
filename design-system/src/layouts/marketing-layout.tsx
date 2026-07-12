import { cn } from "../utils";
import { BackgroundLayers } from "../backgrounds";

export function MarketingLayout({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("relative min-h-dvh overflow-hidden bg-background text-white", className)}>
      <BackgroundLayers />
      <main className="relative z-10">{children}</main>
    </div>
  );
}
