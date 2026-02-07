import { motion } from "framer-motion";
import { useState } from "react";
import { ChevronRight, ExternalLink, AlertCircle, CheckCircle, HelpCircle } from "lucide-react";

interface Claim {
  id: number;
  text: string;
  status: "supported" | "contradicted" | "unverifiable";
  confidence: number;
  source?: string;
  sourceSnippet?: string;
  explanation?: string;
  correction?: string;
}

const sampleClaims: Claim[] = [
  {
    id: 1,
    text: "The patient was diagnosed with Type 2 Diabetes in March 2024.",
    status: "supported",
    confidence: 95,
    source: "Patient Record B, Page 4",
    sourceSnippet: "Diagnosis confirmed: Type 2 Diabetes Mellitus, dated March 15, 2024.",
    explanation: "Direct match found in patient records with exact date correlation.",
  },
  {
    id: 2,
    text: "The prescribed medication was Metformin 500mg twice daily.",
    status: "supported",
    confidence: 92,
    source: "Prescription Log, Entry #2847",
    sourceSnippet: "Rx: Metformin Hydrochloride 500mg, Sig: 1 tab PO BID",
    explanation: "Prescription details match the generated summary exactly.",
  },
  {
    id: 3,
    text: "The patient reported no history of cardiovascular disease.",
    status: "contradicted",
    confidence: 88,
    source: "Patient Record B, Page 2",
    sourceSnippet: "Past Medical History: Hypertension (2019), Mild atrial fibrillation (2022)",
    explanation: "The source documents indicate a history of hypertension and atrial fibrillation, which are cardiovascular conditions.",
    correction: "The patient has a documented history of cardiovascular conditions including hypertension (2019) and mild atrial fibrillation (2022).",
  },
  {
    id: 4,
    text: "Lab results showed an HbA1c level of 7.2%.",
    status: "supported",
    confidence: 98,
    source: "Lab Report #LR-9842, Section 3",
    sourceSnippet: "Hemoglobin A1c (HbA1c): 7.2% [Reference range: 4.0-5.6%]",
    explanation: "Exact value match found in laboratory reports.",
  },
  {
    id: 5,
    text: "The patient was referred to a specialist at City General Hospital.",
    status: "unverifiable",
    confidence: 35,
    explanation: "No referral documentation found in the provided source documents. This claim cannot be verified or denied.",
  },
  {
    id: 6,
    text: "Follow-up appointment was scheduled for 3 months later.",
    status: "supported",
    confidence: 78,
    source: "Clinical Notes, Page 6",
    sourceSnippet: "Schedule 3-month follow-up for HbA1c re-check and medication review.",
    explanation: "Follow-up scheduling aligns with clinical notes.",
  },
];

function ClaimStatusIcon({ status }: { status: string }) {
  switch (status) {
    case "supported": return <CheckCircle className="h-4 w-4 text-claim-supported flex-shrink-0" />;
    case "contradicted": return <AlertCircle className="h-4 w-4 text-claim-contradicted flex-shrink-0" />;
    case "unverifiable": return <HelpCircle className="h-4 w-4 text-claim-unverifiable flex-shrink-0" />;
    default: return null;
  }
}

function getClaimClass(status: string) {
  switch (status) {
    case "supported": return "claim-supported";
    case "contradicted": return "claim-contradicted";
    case "unverifiable": return "claim-unverifiable";
    default: return "";
  }
}

export function DocumentViewer() {
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 h-full">
      {/* Annotated Document */}
      <div className="lg:col-span-3 bg-glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-sm font-medium text-muted-foreground">Annotated Document</h3>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-claim-supported" />
              <span className="text-xs text-muted-foreground">Supported</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-claim-contradicted" />
              <span className="text-xs text-muted-foreground">Contradicted</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-claim-unverifiable" />
              <span className="text-xs text-muted-foreground">Unverifiable</span>
            </div>
          </div>
        </div>
        <div className="space-y-2 overflow-y-auto max-h-[600px] scrollbar-thin pr-2">
          {sampleClaims.map((claim, index) => (
            <motion.div
              key={claim.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.05 * index }}
              className={`${getClaimClass(claim.status)} rounded-lg p-4 cursor-pointer transition-all hover:brightness-110 ${
                selectedClaim?.id === claim.id ? "ring-1 ring-primary" : ""
              }`}
              onClick={() => setSelectedClaim(claim)}
            >
              <div className="flex items-start gap-3">
                <ClaimStatusIcon status={claim.status} />
                <div className="flex-1">
                  <p className="text-sm text-foreground leading-relaxed">{claim.text}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-mono text-muted-foreground">
                      Confidence: {claim.confidence}%
                    </span>
                    {claim.source && (
                      <>
                        <span className="text-muted-foreground">·</span>
                        <span className="text-xs text-primary">{claim.source}</span>
                      </>
                    )}
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Citation Panel */}
      <div className="lg:col-span-2 bg-glass rounded-xl p-6">
        <h3 className="text-sm font-medium text-muted-foreground mb-5">Citation & Evidence</h3>
        {selectedClaim ? (
          <motion.div
            key={selectedClaim.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-5"
          >
            <div>
              <div className="flex items-center gap-2 mb-2">
                <ClaimStatusIcon status={selectedClaim.status} />
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {selectedClaim.status}
                </span>
              </div>
              <p className="text-sm text-foreground leading-relaxed">{selectedClaim.text}</p>
            </div>

            {/* Confidence */}
            <div>
              <p className="text-xs text-muted-foreground mb-2">Confidence Level</p>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <motion.div
                  className={`h-full rounded-full ${
                    selectedClaim.status === "supported" ? "bg-claim-supported" :
                    selectedClaim.status === "contradicted" ? "bg-claim-contradicted" :
                    "bg-claim-unverifiable"
                  }`}
                  initial={{ width: 0 }}
                  animate={{ width: `${selectedClaim.confidence}%` }}
                  transition={{ duration: 0.6 }}
                />
              </div>
              <p className="text-xs font-mono text-muted-foreground mt-1">{selectedClaim.confidence}%</p>
            </div>

            {/* Source Snippet */}
            {selectedClaim.sourceSnippet && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Source Evidence</p>
                <div className="bg-secondary/50 border border-border rounded-lg p-3">
                  <p className="text-xs text-foreground italic leading-relaxed">"{selectedClaim.sourceSnippet}"</p>
                  {selectedClaim.source && (
                    <div className="flex items-center gap-1.5 mt-2">
                      <ExternalLink className="h-3 w-3 text-primary" />
                      <span className="text-xs text-primary font-medium">{selectedClaim.source}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Explanation */}
            {selectedClaim.explanation && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Explanation</p>
                <p className="text-xs text-foreground/80 leading-relaxed">{selectedClaim.explanation}</p>
              </div>
            )}

            {/* Correction */}
            {selectedClaim.correction && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Suggested Correction</p>
                <div className="bg-claim-supported-bg border border-claim-supported/20 rounded-lg p-3">
                  <p className="text-xs text-foreground leading-relaxed">{selectedClaim.correction}</p>
                </div>
              </div>
            )}
          </motion.div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center mb-3">
              <ExternalLink className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">Click on a claim to view its citation and evidence</p>
          </div>
        )}
      </div>
    </div>
  );
}
