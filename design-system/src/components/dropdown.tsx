import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { Check, ChevronRight } from "lucide-react";
import { cn } from "../utils";

export const Dropdown = DropdownMenu.Root;
export const DropdownTrigger = DropdownMenu.Trigger;
export const DropdownGroup = DropdownMenu.Group;

export function DropdownContent({ className, ...props }: React.ComponentPropsWithoutRef<typeof DropdownMenu.Content>) {
  return (
    <DropdownMenu.Portal>
      <DropdownMenu.Content
        sideOffset={8}
        className={cn("z-50 min-w-48 rounded-ds-lg border border-white/10 bg-elevated p-1 shadow-popover", className)}
        {...props}
      />
    </DropdownMenu.Portal>
  );
}

export function DropdownItem({ className, ...props }: React.ComponentPropsWithoutRef<typeof DropdownMenu.Item>) {
  return <DropdownMenu.Item className={cn("flex cursor-pointer select-none items-center gap-2 rounded-ds px-3 py-2 text-sm text-slate-200 outline-none transition-colors hover:bg-white/[0.05] focus:bg-white/[0.05]", className)} {...props} />;
}

export function DropdownCheckboxItem({ className, children, ...props }: React.ComponentPropsWithoutRef<typeof DropdownMenu.CheckboxItem>) {
  return (
    <DropdownMenu.CheckboxItem className={cn("flex cursor-pointer select-none items-center gap-2 rounded-ds px-3 py-2 text-sm text-slate-200 outline-none focus:bg-white/[0.05]", className)} {...props}>
      <DropdownMenu.ItemIndicator>
        <Check aria-hidden="true" className="h-4 w-4" />
      </DropdownMenu.ItemIndicator>
      {children}
    </DropdownMenu.CheckboxItem>
  );
}

export function DropdownSubTrigger({ className, children, ...props }: React.ComponentPropsWithoutRef<typeof DropdownMenu.SubTrigger>) {
  return (
    <DropdownMenu.SubTrigger className={cn("flex cursor-pointer select-none items-center justify-between gap-2 rounded-ds px-3 py-2 text-sm text-slate-200 outline-none focus:bg-white/[0.05]", className)} {...props}>
      {children}
      <ChevronRight aria-hidden="true" className="h-4 w-4" />
    </DropdownMenu.SubTrigger>
  );
}
