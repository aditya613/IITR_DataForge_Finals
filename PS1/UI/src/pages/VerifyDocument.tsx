import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { DocumentViewer } from "@/components/document/DocumentViewer";

const VerifyDocument = () => {
  return (
    <DashboardLayout title="Verify Document" subtitle="Analyze LLM-generated text against trusted sources">
      <DocumentViewer />
    </DashboardLayout>
  );
};

export default VerifyDocument;
