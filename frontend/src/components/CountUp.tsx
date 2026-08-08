import React, { useEffect, useState } from "react";

interface CountUpProps {
  value: number;
  duration?: number;
}

export const CountUp: React.FC<CountUpProps> = ({ value, duration = 500 }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    // Respect prefers-reduced-motion configuration
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setDisplayValue(value);
      return;
    }

    let startTimestamp: number | null = null;
    const startValue = displayValue;
    const diff = value - startValue;

    let animFrameId: number;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      setDisplayValue(Math.floor(startValue + diff * progress));
      if (progress < 1) {
        animFrameId = window.requestAnimationFrame(step);
      }
    };

    animFrameId = window.requestAnimationFrame(step);
    return () => {
      window.cancelAnimationFrame(animFrameId);
    };
  }, [value, duration]);

  return <>{displayValue}</>;
};

export default CountUp;
