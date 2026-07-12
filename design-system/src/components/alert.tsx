import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";
import { cn } from "../utils";

const icons = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: XCircle
};

const tones = {
  info: "border-primary/25 bg-primary/10 text-blue-100",
  success: "border-success/25 bg-success/10 text-emerald-100",
  warning: "border-warning/25 bg-warning/10 text-amber-100",
  danger: "border-danger/25 bg-danger/10 text-red-100"
};

export function Alert({
  tone = "info",
  title,
  children,
  className
}: {
  tone?: keyof typeof tones;
  title: string;
  children?: React.ReactNode;
  className?: string;
}) {
  const Icon = icons[tone];
  return (
    <div role="status" className={cn("flex gap-3 rounded-ds border p-4 text-sm", tones[tone], className)}>
      <Icon aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0" />
      <div>
        <div className="font-semibold">{title}</div>
        {children ? <div className="mt-1 text-slate-300">{children}</div> : null}
      </div>
    </div>
  );
}
