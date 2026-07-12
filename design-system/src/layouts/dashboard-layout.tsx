import { cn } from "../utils";

export function DashboardLayout({
  sidebar,
  topbar,
  children,
  className
}: {
  sidebar?: React.ReactNode;
  topbar?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className="min-h-dvh bg-background text-white">
      <div className="flex min-h-dvh">
        {sidebar}
        <div className="min-w-0 flex-1">
          {topbar}
          <main className={cn("mx-auto w-full max-w-[1440px] px-6 py-8 lg:px-8", className)}>{children}</main>
        </div>
      </div>
    </div>
  );
}
