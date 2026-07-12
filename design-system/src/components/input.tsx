import { forwardRef } from "react";
import { Search, X } from "lucide-react";
import { cn } from "../utils";
import { Button } from "./button";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = forwardRef<HTMLInputElement, InputProps>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "h-10 w-full rounded-ds border border-white/10 bg-white/[0.03] px-3 text-sm text-white placeholder:text-slate-500 transition-colors focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
  />
));
Input.displayName = "Input";

export function SearchBar({
  value,
  onChange,
  onClear,
  placeholder = "Search DcoY..."
}: {
  value: string;
  onChange: (value: string) => void;
  onClear?: () => void;
  placeholder?: string;
}) {
  return (
    <div className="relative">
      <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
      <Input
        aria-label={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="pl-9 pr-10"
      />
      {value ? (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label="Clear search"
          className="absolute right-0 top-0 h-10 w-10"
          onClick={onClear}
        >
          <X aria-hidden="true" className="h-4 w-4" />
        </Button>
      ) : null}
    </div>
  );
}
