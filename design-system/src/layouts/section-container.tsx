import { cn } from "../utils";

export function SectionContainer({
  children,
  size = "xl",
  className
}: {
  children: React.ReactNode;
  size?: "md" | "lg" | "xl" | "2xl" | "full";
  className?: string;
}) {
  const sizes = {
    md: "max-w-3xl",
    lg: "max-w-5xl",
    xl: "max-w-7xl",
    "2xl": "max-w-[1440px]",
    full: "max-w-none"
  };
  return <section className={cn("mx-auto w-full px-6 py-16 lg:px-8", sizes[size], className)}>{children}</section>;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}) {
  return (
    <header className={cn("mb-8 flex flex-col gap-6 border-b border-white/10 pb-8 lg:flex-row lg:items-end lg:justify-between", className)}>
      <div>
        {eyebrow ? <div className="mb-3 text-xs font-semibold uppercase tracking-[0.08em] text-accent">{eyebrow}</div> : null}
        <h1 className="max-w-5xl text-4xl font-bold leading-tight text-white lg:text-5xl">{title}</h1>
        {description ? <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300">{description}</p> : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap gap-3">{actions}</div> : null}
    </header>
  );
}
