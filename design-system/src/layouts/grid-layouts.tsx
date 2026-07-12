import { cn } from "../utils";

export function ContentGrid({
  children,
  columns = 12,
  className
}: {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4 | 6 | 12;
  className?: string;
}) {
  const columnClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 lg:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 xl:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 xl:grid-cols-4",
    6: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6",
    12: "grid-cols-1 lg:grid-cols-12"
  };
  return <div className={cn("grid gap-6", columnClasses[columns], className)}>{children}</div>;
}

export function SidebarLayout({
  sidebar,
  children,
  reverse,
  className
}: {
  sidebar: React.ReactNode;
  children: React.ReactNode;
  reverse?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]", reverse && "lg:grid-cols-[minmax(0,1fr)_320px]", className)}>
      {reverse ? (
        <>
          <div>{children}</div>
          <aside>{sidebar}</aside>
        </>
      ) : (
        <>
          <aside>{sidebar}</aside>
          <div>{children}</div>
        </>
      )}
    </div>
  );
}

export function SplitPanelLayout({ left, right, className }: { left: React.ReactNode; right: React.ReactNode; className?: string }) {
  return <div className={cn("grid gap-6 lg:grid-cols-2", className)}><div>{left}</div><div>{right}</div></div>;
}

export function WidgetLayout({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("grid gap-6 sm:grid-cols-2 xl:grid-cols-4", className)}>{children}</div>;
}
