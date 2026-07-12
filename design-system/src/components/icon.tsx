import { cn } from "../utils";

export type IconComponent = React.ComponentType<{
  className?: string;
  strokeWidth?: number;
  "aria-hidden"?: boolean | "true" | "false";
}>;

export function IconFrame({
  icon: Icon,
  label,
  tone = "primary",
  className
}: {
  icon: IconComponent;
  label?: string;
  tone?: "primary" | "secondary" | "accent" | "success" | "warning" | "danger";
  className?: string;
}) {
  return (
    <span
      aria-label={label}
      aria-hidden={label ? undefined : true}
      className={cn("inline-flex h-10 w-10 items-center justify-center rounded-ds border border-white/10 bg-white/[0.03]", className)}
    >
      <Icon className={cn("h-5 w-5", tone === "primary" && "text-primary", tone === "secondary" && "text-secondary", tone === "accent" && "text-accent", tone === "success" && "text-success", tone === "warning" && "text-warning", tone === "danger" && "text-danger")} strokeWidth={2} />
    </span>
  );
}
