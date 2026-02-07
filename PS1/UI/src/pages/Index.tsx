import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { TrustScoreGauge } from "@/components/dashboard/TrustScoreGauge";
import { ClaimsChart } from "@/components/dashboard/ClaimsChart";
import { RecentAnalysis } from "@/components/dashboard/RecentAnalysis";
import { SystemFlowchart } from "@/components/dashboard/SystemFlowchart";
import { FileSearch, Shield, AlertTriangle, Clock } from "lucide-react";

const Index = () => {
  return (
    <DashboardLayout title="Dashboard" subtitle="Monitor your AI fact-checking pipeline">
      <div className="space-y-6 max-w-7xl">
        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Documents Verified"
            value="1,247"
            change="+12% from last week"
            changeType="positive"
            icon={FileSearch}
            delay={0}
          />
          <StatCard
            title="Avg Trust Score"
            value="84.2%"
            change="+3.1% improvement"
            changeType="positive"
            icon={Shield}
            iconColor="text-claim-supported"
            delay={0.1}
          />
          <StatCard
            title="Hallucinations Caught"
            value="342"
            change="27.4% detection rate"
            changeType="negative"
            icon={AlertTriangle}
            iconColor="text-claim-contradicted"
            delay={0.2}
          />
          <StatCard
            title="Avg Processing Time"
            value="2.3s"
            change="-0.4s vs last month"
            changeType="positive"
            icon={Clock}
            delay={0.3}
          />
        </div>

        {/* Trust Score + Pipeline */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <TrustScoreGauge score={84} />
          <div className="lg:col-span-2">
            <SystemFlowchart />
          </div>
        </div>

        {/* Charts */}
        <ClaimsChart />

        {/* Recent Analysis */}
        <RecentAnalysis />
      </div>
    </DashboardLayout>
  );
};

export default Index;
