import type { LucideIcon } from "lucide-react";
import { Brain, FileSearch, Radar, ShieldAlert } from "lucide-react";
import { Badge } from "./badge";
import { Card, CardDescription, CardHeader, CardTitle } from "./card";
import { cn } from "../utils";

function DomainCard({
  icon: Icon,
  title,
  description,
  meta,
  tone = "primary",
  className
}: {
  icon: LucideIcon;
  title: string;
  description?: string;
  meta?: React.ReactNode;
  tone?: "primary" | "secondary" | "accent" | "success" | "warning" | "danger";
  className?: string;
}) {
  return (
    <Card interactive spotlight className={cn("space-y-4", className)}>
      <CardHeader className="mb-0">
        <div>
          <div className="mb-4 inline-flex rounded-ds border border-white/10 bg-white/[0.03] p-2">
            <Icon aria-hidden="true" className="h-5 w-5 text-primary" />
          </div>
          <CardTitle>{title}</CardTitle>
          {description ? <CardDescription className="mt-2">{description}</CardDescription> : null}
        </div>
        <Badge variant={tone}>{meta}</Badge>
      </CardHeader>
    </Card>
  );
}

export function ThreatCard(props: Omit<React.ComponentProps<typeof DomainCard>, "icon">) {
  return <DomainCard icon={ShieldAlert} {...props} />;
}

export function InvestigationCard(props: Omit<React.ComponentProps<typeof DomainCard>, "icon">) {
  return <DomainCard icon={FileSearch} tone="warning" {...props} />;
}

export function RuleCard(props: Omit<React.ComponentProps<typeof DomainCard>, "icon">) {
  return <DomainCard icon={Radar} tone="accent" {...props} />;
}

export function AIChatBubble({
  role,
  children,
  confidence
}: {
  role: "user" | "assistant";
  children: React.ReactNode;
  confidence?: string;
}) {
  const isAssistant = role === "assistant";
  return (
    <div className={cn("flex", isAssistant ? "justify-start" : "justify-end")}>
      <div className={cn("max-w-[78%] rounded-ds-lg border px-4 py-3 text-sm leading-6", isAssistant ? "border-white/10 bg-card text-slate-200" : "border-primary/30 bg-primary text-white")}>
        <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.04em] opacity-80">
          {isAssistant ? <Brain aria-hidden="true" className="h-3.5 w-3.5" /> : null}
          {role}
          {confidence ? <Badge variant="success">{confidence}</Badge> : null}
        </div>
        {children}
      </div>
    </div>
  );
}

export function SOCWidget({ title, children, className }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <Card className={cn("min-h-[260px]", className)}>
      <div className="mb-4 text-xs font-semibold uppercase tracking-[0.04em] text-slate-400">{title}</div>
      {children}
    </Card>
  );
}
