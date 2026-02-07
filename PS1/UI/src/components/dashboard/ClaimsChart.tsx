import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const pieData = [
  { name: "Supported", value: 42, color: "hsl(152, 60%, 48%)" },
  { name: "Contradicted", value: 8, color: "hsl(0, 72%, 58%)" },
  { name: "Unverifiable", value: 12, color: "hsl(38, 80%, 56%)" },
];

const barData = [
  { domain: "Medical", supported: 85, contradicted: 8, unverifiable: 7 },
  { domain: "Legal", supported: 78, contradicted: 12, unverifiable: 10 },
  { domain: "Finance", supported: 91, contradicted: 4, unverifiable: 5 },
  { domain: "Technical", supported: 82, contradicted: 10, unverifiable: 8 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
      <p className="text-sm font-medium text-foreground mb-1">{label}</p>
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-xs text-muted-foreground">
          <span style={{ color: entry.color }}>●</span> {entry.name}: {entry.value}%
        </p>
      ))}
    </div>
  );
};

export function ClaimsChart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-glass rounded-xl p-6"
    >
      <h3 className="text-sm font-medium text-muted-foreground mb-6">Claims Breakdown</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="flex flex-col items-center">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={4}
                dataKey="value"
                strokeWidth={0}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="flex items-center gap-5 mt-2">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-xs text-muted-foreground">{item.name} ({item.value})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar Chart */}
        <div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={barData} barGap={2}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 14%, 18%)" />
              <XAxis dataKey="domain" tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "hsl(215, 12%, 52%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="supported" name="Supported" fill="hsl(152, 60%, 48%)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="contradicted" name="Contradicted" fill="hsl(0, 72%, 58%)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="unverifiable" name="Unverifiable" fill="hsl(38, 80%, 56%)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
}
