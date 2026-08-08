import React from "react";

interface GlassPanelProps {
  children?: React.ReactNode;
  className?: string;
  borderColor?: "amber" | "cyan" | "gray" | "red" | "none";
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
    amber: "border-[rgba(245,166,35,0.14)] shadow-[0_0_12px_rgba(245,166,35,0.05),inset_0_0_0_1px_rgba(245,166,35,0.08)]",
    cyan: "border-[rgba(0,229,255,0.14)] shadow-[0_0_12px_rgba(0,229,255,0.05),inset_0_0_0_1px_rgba(0,229,255,0.08)]",
    red: "border-[rgba(239,68,68,0.4)] shadow-[0_0_25px_rgba(239,68,68,0.25),inset_0_0_0_1px_rgba(239,68,68,0.25)]",
    gray: "border-[rgba(255,255,255,0.08)] shadow-none",
    none: "border-transparent shadow-none",
  };

  const bracketColorClasses = {
    amber: "text-amber-500/35",
    cyan: "text-cyan-500/35",
    gray: "text-gray-500/25",
    red: "text-red-500/75",
    none: "text-transparent",
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
        <svg
          className={`absolute top-3 left-3 w-3 h-3 ${bracketColorClasses[borderColor]} pointer-events-none`}
          viewBox="0 0 12 12"
          fill="none"
        >
          <path d="M12,2 H2 V12" stroke="currentColor" strokeWidth="2" strokeLinecap="square" />
        </svg>
      )}

      {/* Main Content */}
      <div className="relative z-10 w-full h-full">
        {children}
      </div>

      {/* Corner Bracket - Bottom Right */}
      {showBrackets && (
        <svg
          className={`absolute bottom-3 right-3 w-3 h-3 ${bracketColorClasses[borderColor]} pointer-events-none`}
          viewBox="0 0 12 12"
          fill="none"
        >
          <path d="M0,10 H10 V0" stroke="currentColor" strokeWidth="2" strokeLinecap="square" />
        </svg>
      )}
    </div>
  );

};
