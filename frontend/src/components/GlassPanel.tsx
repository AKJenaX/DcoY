import React from "react";

interface GlassPanelProps {
  children?: React.ReactNode;
  className?: string;
  borderColor?: "amber" | "cyan" | "gray" | "none";
  showBrackets?: boolean;
  onClick?: () => void;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  children,
  className = "",
  borderColor = "amber",
  showBrackets = true,
  onClick,
}) => {
  const borderClasses = {
    amber: "border-[rgba(245,166,35,0.25)] shadow-[0_0_30px_rgba(245,166,35,0.03)]",
    cyan: "border-[rgba(0,229,255,0.25)] shadow-[0_0_30px_rgba(0,229,255,0.03)]",
    gray: "border-[rgba(255,255,255,0.08)] shadow-none",
    none: "border-transparent shadow-none",
  };

  const bracketColorClasses = {
    amber: "border-amber-500/60",
    cyan: "border-cyan-500/60",
    gray: "border-gray-500/40",
    none: "border-transparent",
  };

  return (
    <div
      onClick={onClick}
      className={`relative bg-[rgba(8,8,12,0.45)] rounded-2xl border backdrop-blur-md saturate-[180%] ${borderClasses[borderColor]} ${className}`}
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
