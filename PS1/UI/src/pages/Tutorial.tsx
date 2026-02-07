import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { TutorialSection } from "@/components/tutorial/TutorialSection";

const Tutorial = () => {
  return (
    <DashboardLayout title="Tutorial" subtitle="Learn how to use HalluciGuard effectively">
      <div className="max-w-5xl">
        <TutorialSection />
      </div>
    </DashboardLayout>
  );
};

export default Tutorial;
