import { motion } from "framer-motion";
import { ArrowRight, FileText, Cpu, Search, CheckCircle, AlertTriangle, BarChart3 } from "lucide-react";

const steps = [
  {
    icon: FileText,
    label: "Source Documents",
    description: "Ingest trusted knowledge base",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    icon: Cpu,
    label: "Claim Decomposition",
    description: "Break into atomic claims",
    color: "text-chart-5",
    bgColor: "bg-chart-5/10",
  },
  {
    icon: Search,
    label: "RAG Verification",
    description: "Cross-reference with sources",
    color: "text-claim-unverifiable",
    bgColor: "bg-claim-unverifiable-bg",
  },
  {
    icon: CheckCircle,
    label: "Classification",
    description: "Supported / Contradicted / Unverifiable",
    color: "text-claim-supported",
    bgColor: "bg-claim-supported-bg",
  },
  {
    icon: AlertTriangle,
    label: "Citation & Correction",
    description: "Link claims to evidence",
    color: "text-claim-contradicted",
    bgColor: "bg-claim-contradicted-bg",
  },
  {
    icon: BarChart3,
    label: "Trust Score",
    description: "Generate confidence report",
    color: "text-trust-high",
    bgColor: "bg-trust-high/10",
  },
];

export function SystemFlowchart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className="bg-glass rounded-xl p-6"
    >
      <h3 className="text-sm font-medium text-muted-foreground mb-6">System Pipeline</h3>
      <div className="flex items-center justify-between overflow-x-auto pb-2 scrollbar-thin gap-1">
        {steps.map((step, index) => (
          <div key={step.label} className="flex items-center flex-shrink-0">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 * index + 0.4, duration: 0.3 }}
              className="flex flex-col items-center text-center w-28"
            >
              <div className={`h-12 w-12 rounded-xl ${step.bgColor} flex items-center justify-center mb-2 border border-border`}>
                <step.icon className={`h-5 w-5 ${step.color}`} />
              </div>
              <p className="text-xs font-semibold text-foreground leading-tight">{step.label}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5 leading-tight">{step.description}</p>
            </motion.div>
            {index < steps.length - 1 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 * index + 0.5 }}
              >
                <ArrowRight className="h-4 w-4 text-border mx-1 flex-shrink-0" />
              </motion.div>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );
}
