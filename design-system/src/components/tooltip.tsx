import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { cn } from "../utils";

export const TooltipProvider = TooltipPrimitive.Provider;
export const Tooltip = TooltipPrimitive.Root;
export const TooltipTrigger = TooltipPrimitive.Trigger;

export function TooltipContent({ className, ...props }: React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>) {
  return (
    <TooltipPrimitive.Portal>
      <TooltipPrimitive.Content
        sideOffset={8}
        className={cn("z-50 max-w-xs rounded-ds border border-white/10 bg-elevated px-3 py-2 text-xs text-slate-200 shadow-popover", className)}
        {...props}
      />
    </TooltipPrimitive.Portal>
  );
}
