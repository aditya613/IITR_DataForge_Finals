import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { motion } from "framer-motion";
import { Upload, FileText, CheckCircle, X, Plus } from "lucide-react";
import { useState } from "react";

const existingSources = [
  { id: 1, name: "Medical Guidelines 2024.pdf", size: "2.4 MB", pages: 48, status: "indexed" },
  { id: 2, name: "Patient Records - Case #4521.pdf", size: "1.1 MB", pages: 12, status: "indexed" },
  { id: 3, name: "Drug Interaction Database v3.2.csv", size: "856 KB", pages: null, status: "indexed" },
  { id: 4, name: "Clinical Trial Results - Phase III.pdf", size: "5.2 MB", pages: 134, status: "processing" },
];

const Sources = () => {
  const [isDragging, setIsDragging] = useState(false);

  return (
    <DashboardLayout title="Upload Sources" subtitle="Manage your trusted knowledge base documents">
      <div className="space-y-6 max-w-4xl">
        {/* Upload Area */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className={`bg-glass rounded-xl p-12 border-2 border-dashed transition-all cursor-pointer text-center ${
            isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={() => setIsDragging(false)}
        >
          <div className="flex flex-col items-center gap-4">
            <div className="h-14 w-14 rounded-xl bg-primary/10 flex items-center justify-center">
              <Upload className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Drop files here or click to browse</p>
              <p className="text-xs text-muted-foreground mt-1">
                Supports PDF, TXT, DOCX, CSV — Max 50MB per file
              </p>
            </div>
            <button className="mt-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors">
              <Plus className="h-4 w-4 inline mr-1.5" />
              Select Files
            </button>
          </div>
        </motion.div>

        {/* Existing Sources */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-glass rounded-xl p-6"
        >
          <h3 className="text-sm font-medium text-muted-foreground mb-4">Knowledge Base ({existingSources.length} documents)</h3>
          <div className="space-y-2">
            {existingSources.map((source, index) => (
              <motion.div
                key={source.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * index + 0.1 }}
                className="flex items-center gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors group"
              >
                <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">{source.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-muted-foreground">{source.size}</span>
                    {source.pages && (
                      <>
                        <span className="text-muted-foreground">·</span>
                        <span className="text-xs text-muted-foreground">{source.pages} pages</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {source.status === "indexed" ? (
                    <span className="flex items-center gap-1 text-xs text-claim-supported">
                      <CheckCircle className="h-3.5 w-3.5" /> Indexed
                    </span>
                  ) : (
                    <span className="text-xs text-claim-unverifiable animate-pulse-glow">Processing...</span>
                  )}
                  <button className="h-7 w-7 rounded-lg bg-secondary flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-claim-contradicted">
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default Sources;
