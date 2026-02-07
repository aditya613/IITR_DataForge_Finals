import { motion } from "framer-motion";
import { Play, Clock, BookOpen, ChevronRight, ExternalLink } from "lucide-react";
import { useState } from "react";

const tutorials = [
  {
    id: 1,
    title: "Getting Started with HalluciGuard",
    description: "Learn how to upload source documents and verify your first LLM-generated text.",
    duration: "5:32",
    thumbnail: "getting-started",
    category: "Basics",
  },
  {
    id: 2,
    title: "Understanding Trust Scores",
    description: "Deep dive into how trust scores are calculated and what they mean for your workflow.",
    duration: "8:15",
    thumbnail: "trust-scores",
    category: "Analytics",
  },
  {
    id: 3,
    title: "Reading Citation Reports",
    description: "How to interpret color-coded annotations and trace claims back to source documents.",
    duration: "6:48",
    thumbnail: "citation-reports",
    category: "Verification",
  },
  {
    id: 4,
    title: "Batch Document Processing",
    description: "Process multiple documents at once and compare verification results across domains.",
    duration: "4:20",
    thumbnail: "batch-processing",
    category: "Advanced",
  },
  {
    id: 5,
    title: "API Integration Guide",
    description: "Connect HalluciGuard to your existing pipeline using our REST API endpoints.",
    duration: "10:05",
    thumbnail: "api-integration",
    category: "Developer",
  },
  {
    id: 6,
    title: "Custom Knowledge Base Setup",
    description: "Configure domain-specific knowledge bases for healthcare, legal, or finance use cases.",
    duration: "7:30",
    thumbnail: "knowledge-base",
    category: "Configuration",
  },
];

const categoryColors: Record<string, string> = {
  Basics: "bg-primary/10 text-primary",
  Analytics: "bg-claim-supported-bg text-claim-supported",
  Verification: "bg-claim-unverifiable-bg text-claim-unverifiable",
  Advanced: "bg-chart-5/10 text-chart-5",
  Developer: "bg-claim-contradicted-bg text-claim-contradicted",
  Configuration: "bg-secondary text-secondary-foreground",
};

export function TutorialSection() {
  const [selectedTutorial, setSelectedTutorial] = useState(tutorials[0]);

  return (
    <div className="space-y-6">
      {/* Featured Video Player */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-glass rounded-xl overflow-hidden"
      >
        <div className="aspect-video bg-secondary/50 relative flex items-center justify-center group cursor-pointer">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/80" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="h-20 w-20 rounded-full bg-primary/20 border-2 border-primary flex items-center justify-center glow-primary group-hover:bg-primary/30 transition-colors"
              >
                <Play className="h-8 w-8 text-primary ml-1" />
              </motion.div>
              <div className="text-center">
                <p className="font-display text-lg font-semibold text-foreground">{selectedTutorial.title}</p>
                <p className="text-sm text-muted-foreground mt-1">{selectedTutorial.description}</p>
              </div>
            </div>
          </div>
          <div className="absolute bottom-4 left-4 flex items-center gap-2">
            <div className={`px-2 py-0.5 rounded text-xs font-medium ${categoryColors[selectedTutorial.category] || ""}`}>
              {selectedTutorial.category}
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span className="text-xs">{selectedTutorial.duration}</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Tutorial Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tutorials.map((tutorial, index) => (
          <motion.div
            key={tutorial.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * index }}
            onClick={() => setSelectedTutorial(tutorial)}
            className={`bg-glass rounded-xl p-4 cursor-pointer transition-all hover:border-primary/30 group ${
              selectedTutorial.id === tutorial.id ? "border-primary/50 glow-primary" : ""
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0 group-hover:bg-primary/10 transition-colors">
                <Play className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground leading-tight">{tutorial.title}</p>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{tutorial.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${categoryColors[tutorial.category] || ""}`}>
                    {tutorial.category}
                  </div>
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {tutorial.duration}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Documentation Link */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="bg-glass rounded-xl p-5 flex items-center justify-between group cursor-pointer hover:border-primary/30 transition-all"
      >
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <BookOpen className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">Full Documentation</p>
            <p className="text-xs text-muted-foreground">Explore API docs, guides, and best practices</p>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
      </motion.div>
    </div>
  );
}
