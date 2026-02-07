import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { motion } from "framer-motion";
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const trendData = [
  { date: "Jan", trustScore: 72, documents: 85, hallucinations: 38 },
  { date: "Feb", trustScore: 74, documents: 102, hallucinations: 35 },
  { date: "Mar", trustScore: 78, documents: 134, hallucinations: 31 },
  { date: "Apr", trustScore: 76, documents: 158, hallucinations: 42 },
  { date: "May", trustScore: 81, documents: 189, hallucinations: 28 },
  { date: "Jun", trustScore: 84, documents: 211, hallucinations: 24 },
  { date: "Jul", trustScore: 82, documents: 245, hallucinations: 30 },
  { date: "Aug", trustScore: 86, documents: 268, hallucinations: 22 },
];

const domainData = [
  { domain: "Healthcare", accuracy: 87, volume: 420 },
  { domain: "Legal", accuracy: 78, volume: 312 },
  { domain: "Finance", accuracy: 92, volume: 285 },
  { domain: "Technical", accuracy: 84, volume: 230 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
      <p className="text-sm font-medium text-foreground mb-1">{label}</p>
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-xs text-muted-foreground">
          <span style={{ color: entry.color }}>●</span> {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
};

const Analytics = () => {
  return (
    <DashboardLayout title="Analytics" subtitle="Performance trends and insights">
      <div className="space-y-6 max-w-7xl">
        {/* Trust Score Trend */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-glass rounded-xl p-6"
        >
          <h3 className="text-sm font-medium text-muted-foreground mb-6">Trust Score Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="trustGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(185, 72%, 48%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(185, 72%, 48%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 14%, 18%)" />
              <XAxis dataKey="date" tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[60, 100]} tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="trustScore" name="Trust Score" stroke="hsl(185, 72%, 48%)" fill="url(#trustGradient)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Documents Processed */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-glass rounded-xl p-6"
          >
            <h3 className="text-sm font-medium text-muted-foreground mb-6">Documents Processed</h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="docsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(152, 60%, 48%)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(152, 60%, 48%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 14%, 18%)" />
                <XAxis dataKey="date" tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="documents" name="Documents" stroke="hsl(152, 60%, 48%)" fill="url(#docsGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Hallucinations Detected */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-glass rounded-xl p-6"
          >
            <h3 className="text-sm font-medium text-muted-foreground mb-6">Hallucinations Detected</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 14%, 18%)" />
                <XAxis dataKey="date" tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="hallucinations" name="Hallucinations" stroke="hsl(0, 72%, 58%)" strokeWidth={2} dot={{ r: 4, fill: "hsl(0, 72%, 58%)" }} />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Domain Performance */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-glass rounded-xl p-6"
        >
          <h3 className="text-sm font-medium text-muted-foreground mb-6">Domain Performance</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {domainData.map((domain, index) => (
              <motion.div
                key={domain.domain}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 * index + 0.3 }}
                className="bg-secondary/50 rounded-lg p-4 border border-border"
              >
                <p className="text-sm font-medium text-foreground">{domain.domain}</p>
                <div className="mt-3">
                  <div className="flex items-end justify-between mb-1">
                    <span className="text-xs text-muted-foreground">Accuracy</span>
                    <span className="text-sm font-mono font-bold text-claim-supported">{domain.accuracy}%</span>
                  </div>
                  <div className="h-1.5 bg-border rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-claim-supported rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${domain.accuracy}%` }}
                      transition={{ duration: 0.8, delay: 0.1 * index + 0.5 }}
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">{domain.volume} documents</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default Analytics;
