import { Card, CardDescription, CardHeader, CardTitle } from "../components/card";
import { cn } from "../utils";

export function ChartContainer({
  title,
  description,
  actions,
  children,
  className
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn("min-h-[320px]", className)}>
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          {description ? <CardDescription className="mt-1">{description}</CardDescription> : null}
        </div>
        {actions}
      </CardHeader>
      <div className="h-[240px] w-full">{children}</div>
    </Card>
  );
}
