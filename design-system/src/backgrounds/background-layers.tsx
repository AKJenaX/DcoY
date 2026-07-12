import { motion } from "framer-motion";
import { cn } from "../utils";

export function BackgroundLayers({ className }: { className?: string }) {
  return (
    <div aria-hidden="true" className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      <div className="absolute inset-0 bg-background" />
      <div className="dcoy-grid-overlay absolute inset-0 opacity-45" />
      <div className="absolute left-1/2 top-0 h-[520px] w-[720px] -translate-x-1/2 rounded-full bg-primary/10 blur-[120px]" />
      <div className="absolute right-[-160px] top-[30%] h-[380px] w-[380px] rounded-full bg-secondary/10 blur-[110px]" />
      <SoftParticles />
    </div>
  );
}

export function SoftParticles() {
  return (
    <div className="absolute inset-0 opacity-40">
      {Array.from({ length: 18 }).map((_, index) => (
        <motion.span
          key={index}
          className="absolute h-1 w-1 rounded-full bg-white/30"
          style={{
            left: `${(index * 37) % 100}%`,
            top: `${(index * 23) % 100}%`
          }}
          animate={{ opacity: [0.1, 0.45, 0.1], y: [0, -10, 0] }}
          transition={{ duration: 7 + (index % 4), repeat: Infinity, delay: index * 0.2 }}
        />
      ))}
    </div>
  );
}

export function NodeNetwork({ className }: { className?: string }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 640 240" className={cn("h-full w-full text-primary/25", className)}>
      <path d="M42 166L128 92L248 128L356 54L482 120L604 72" fill="none" stroke="currentColor" strokeWidth="1" />
      {[42, 128, 248, 356, 482, 604].map((x, i) => (
        <circle key={x} cx={x} cy={[166, 92, 128, 54, 120, 72][i]} r="5" fill="currentColor" />
      ))}
    </svg>
  );
}

export function GlowLayer({ tone = "primary", className }: { tone?: "primary" | "secondary" | "accent"; className?: string }) {
  const toneClass = tone === "secondary" ? "bg-secondary/10" : tone === "accent" ? "bg-accent/10" : "bg-primary/10";
  return <div aria-hidden="true" className={cn("pointer-events-none absolute h-80 w-80 rounded-full blur-[96px]", toneClass, className)} />;
}
