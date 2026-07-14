import React from "react";

interface GlassPanelProps {
  children?: React.ReactNode;
  className?: string;
  borderColor?: "amber" | "cyan" | "gray" | "none";
  showBrackets?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  children,
  className = "",
  borderColor = "amber",
  showBrackets = true,
  onClick,
  style,
}) => {
  const borderClasses = {
    amber: "border-[rgba(245,166,35,0.25)] shadow-[0_0_25px_rgba(245,166,35,0.12),0_0_50px_rgba(245,166,35,0.06),inset 0 0 0 1px rgba(245,166,35,0.15)]",
    cyan: "border-[rgba(0,229,255,0.25)] shadow-[0_0_25px_rgba(0,229,255,0.12),0_0_50px_rgba(0,229,255,0.06),inset 0 0 0 1px rgba(0,229,255,0.15)]",
    gray: "border-[rgba(255,255,255,0.08)] shadow-none",
    none: "border-transparent shadow-none",
  };

  const bracketColorClasses = {
    amber: "border-amber-500/60",
    cyan: "border-cyan-500/60",
    gray: "border-gray-500/40",
    none: "border-transparent",
  };

  const combinedStyle = {
    backdropFilter: "blur(24px)",
    WebkitBackdropFilter: "blur(24px)",
    background: "linear-gradient(135deg, rgba(245, 166, 35, 0.04) 0%, rgba(0, 0, 0, 0) 50%, rgba(0, 229, 255, 0.04) 100%), rgba(6, 9, 15, 0.65)",
    ...style,
  };

  return (
    <div
      onClick={onClick}
      style={combinedStyle}
      className={`relative rounded-2xl border saturate-[180%] ${borderClasses[borderColor]} ${className}`}
    >
      {/* Corner Bracket - Top Left */}
      {showBrackets && (
        <div
          className={`absolute top-3 left-3 w-3 h-3 border-t-2 border-l-2 ${bracketColorClasses[borderColor]} pointer-events-none`}
        />
      )}

      {/* Main Content */}
      <div className="relative z-10 w-full h-full">
        {children}
      </div>

      {/* Corner Bracket - Bottom Right */}
      {showBrackets && (
        <div
          className={`absolute bottom-3 right-3 w-3 h-3 border-b-2 border-r-2 ${bracketColorClasses[borderColor]} pointer-events-none`}
        />
      )}
    </div>
  );
};
