import { motion } from "framer-motion";
import { FileText, Clock, CheckCircle, AlertTriangle, XCircle } from "lucide-react";

const recentItems = [
  {
    id: 1,
    title: "Patient Medical Summary - Case #4521",
    domain: "Healthcare",
    trustScore: 87,
    claims: { supported: 14, contradicted: 1, unverifiable: 2 },
    time: "2 min ago",
    status: "completed",
  },
  {
    id: 2,
    title: "Q4 Earnings Report Summary",
    domain: "Finance",
    trustScore: 94,
    claims: { supported: 22, contradicted: 0, unverifiable: 1 },
    time: "15 min ago",
    status: "completed",
  },
  {
    id: 3,
    title: "Legal Brief - Johnson v. Corp Inc.",
    domain: "Legal",
    trustScore: 62,
    claims: { supported: 8, contradicted: 4, unverifiable: 3 },
    time: "1 hr ago",
    status: "warning",
  },
  {
    id: 4,
    title: "Technical Manual Rev. 3.2",
    domain: "Technical",
    trustScore: 91,
    claims: { supported: 34, contradicted: 2, unverifiable: 2 },
    time: "3 hrs ago",
    status: "completed",
  },
  {
    id: 5,
    title: "Drug Interaction Analysis Report",
    domain: "Healthcare",
    trustScore: 45,
    claims: { supported: 6, contradicted: 5, unverifiable: 4 },
    time: "5 hrs ago",
    status: "critical",
  },
];

function getStatusIcon(status: string) {
  switch (status) {
    case "completed": return <CheckCircle className="h-4 w-4 text-claim-supported" />;
    case "warning": return <AlertTriangle className="h-4 w-4 text-claim-unverifiable" />;
    case "critical": return <XCircle className="h-4 w-4 text-claim-contradicted" />;
    default: return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

function getScoreColor(score: number) {
  if (score >= 75) return "text-trust-high";
  if (score >= 50) return "text-trust-medium";
  return "text-trust-low";
}

export function RecentAnalysis() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="bg-glass rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-medium text-muted-foreground">Recent Verifications</h3>
        <button className="text-xs text-primary hover:text-primary/80 transition-colors font-medium">
          View all →
        </button>
      </div>
      <div className="space-y-1">
        {recentItems.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * index + 0.3 }}
            className="flex items-center gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors cursor-pointer group"
          >
            <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
              <FileText className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{item.title}</p>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-xs text-muted-foreground">{item.domain}</span>
                <span className="text-muted-foreground">·</span>
                <span className="text-xs text-claim-supported">{item.claims.supported}✓</span>
                <span className="text-xs text-claim-contradicted">{item.claims.contradicted}✗</span>
                <span className="text-xs text-claim-unverifiable">{item.claims.unverifiable}?</span>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <span className={`text-sm font-mono font-bold ${getScoreColor(item.trustScore)}`}>
                {item.trustScore}%
              </span>
              {getStatusIcon(item.status)}
              <span className="text-xs text-muted-foreground">{item.time}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
