import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-pill border px-2.5 py-1 text-xs font-semibold leading-none tracking-[0.02em]",
  {
    variants: {
      variant: {
        default: "border-white/10 bg-white/5 text-slate-200",
        primary: "border-primary/25 bg-primary/10 text-blue-200",
        secondary: "border-secondary/25 bg-secondary/10 text-violet-200",
        accent: "border-accent/25 bg-accent/10 text-cyan-200",
        success: "border-success/25 bg-success/10 text-emerald-200",
        warning: "border-warning/25 bg-warning/10 text-amber-200",
        danger: "border-danger/25 bg-danger/10 text-red-200"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

export type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>;

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export function StatusPill({
  status = "online",
  children,
  className
}: {
  status?: "online" | "warning" | "critical" | "neutral";
  children: React.ReactNode;
  className?: string;
}) {
  const variant = status === "online" ? "success" : status === "warning" ? "warning" : status === "critical" ? "danger" : "default";
  return (
    <Badge variant={variant} className={cn("gap-2", className)}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {children}
    </Badge>
  );
}

export function Tag(props: BadgeProps) {
  return <Badge {...props} />;
}
