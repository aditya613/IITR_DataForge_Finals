import { motion } from "framer-motion";
import { useMemo } from "react";

interface TrustScoreGaugeProps {
  score: number; // 0-100
  label?: string;
}

export function TrustScoreGauge({ score, label = "Overall Trust Score" }: TrustScoreGaugeProps) {
  const circumference = 2 * Math.PI * 70;
  const dashOffset = circumference - (score / 100) * circumference;

  const scoreColor = useMemo(() => {
    if (score >= 75) return "text-trust-high";
    if (score >= 50) return "text-trust-medium";
    return "text-trust-low";
  }, [score]);

  const strokeColor = useMemo(() => {
    if (score >= 75) return "hsl(152, 60%, 48%)";
    if (score >= 50) return "hsl(38, 80%, 56%)";
    return "hsl(0, 72%, 58%)";
  }, [score]);

  const glowColor = useMemo(() => {
    if (score >= 75) return "drop-shadow(0 0 8px hsl(152 60% 48% / 0.5))";
    if (score >= 50) return "drop-shadow(0 0 8px hsl(38 80% 56% / 0.5))";
    return "drop-shadow(0 0 8px hsl(0 72% 58% / 0.5))";
  }, [score]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-glass rounded-xl p-6 flex flex-col items-center"
    >
      <h3 className="text-sm font-medium text-muted-foreground mb-6">{label}</h3>
      <div className="relative w-44 h-44">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke="hsl(220, 14%, 18%)"
            strokeWidth="8"
          />
          <motion.circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke={strokeColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
            style={{ filter: glowColor }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={`text-4xl font-display font-bold ${scoreColor}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {score}%
          </motion.span>
          <span className="text-xs text-muted-foreground mt-1">Confidence</span>
        </div>
      </div>
      <div className="flex items-center gap-4 mt-6">
        <div className="flex items-center gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-trust-high" />
          <span className="text-xs text-muted-foreground">High</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-trust-medium" />
          <span className="text-xs text-muted-foreground">Medium</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-trust-low" />
          <span className="text-xs text-muted-foreground">Low</span>
        </div>
      </div>
    </motion.div>
  );
}
