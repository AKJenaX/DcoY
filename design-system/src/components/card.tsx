import { forwardRef } from "react";
import { motion } from "framer-motion";
import { cn } from "../utils";
import { useSpotlight } from "../hooks";

export type CardProps = React.HTMLAttributes<HTMLDivElement> & {
  interactive?: boolean;
  elevated?: boolean;
  spotlight?: boolean;
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, interactive, elevated, spotlight, onMouseMove, ...props }, ref) => {
    const updateSpotlight = useSpotlight<HTMLDivElement>();
    return (
      <motion.div
        ref={ref}
        onMouseMove={(event) => {
          if (spotlight) updateSpotlight(event);
          onMouseMove?.(event);
        }}
        whileHover={interactive ? { y: -2 } : undefined}
        className={cn(
          "rounded-ds-lg border border-white/10 bg-card bg-[image:var(--dcoy-gradient-surface)] p-6 shadow-card",
          elevated && "bg-elevated shadow-hover",
          interactive && "transition-colors hover:border-primary/30",
          spotlight && "dcoy-spotlight",
          className
        )}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-5 flex items-start justify-between gap-4", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-lg font-semibold text-white", className)} {...props} />;
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm leading-6 text-slate-300", className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("text-sm text-slate-200", className)} {...props} />;
}

export function Panel(props: CardProps) {
  return <Card elevated {...props} />;
}
