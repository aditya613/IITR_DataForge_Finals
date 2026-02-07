import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { motion } from "framer-motion";
import { Save, Bell, Shield, Cpu, Database, Globe } from "lucide-react";

const Settings = () => {
  return (
    <DashboardLayout title="Settings" subtitle="Configure your HalluciGuard instance">
      <div className="space-y-6 max-w-3xl">
        {/* Verification Settings */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-glass rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Shield className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-foreground">Verification Settings</h3>
              <p className="text-xs text-muted-foreground">Configure how claims are verified</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
              <div>
                <p className="text-sm text-foreground">Confidence Threshold</p>
                <p className="text-xs text-muted-foreground">Minimum confidence to mark as supported</p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="50"
                  max="99"
                  defaultValue="75"
                  className="w-24 accent-primary"
                />
                <span className="text-sm font-mono text-primary w-10 text-right">75%</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
              <div>
                <p className="text-sm text-foreground">Strict Mode</p>
                <p className="text-xs text-muted-foreground">Flag unverifiable claims as potential hallucinations</p>
              </div>
              <button className="h-6 w-11 rounded-full bg-primary relative transition-colors">
                <div className="h-5 w-5 rounded-full bg-primary-foreground absolute top-0.5 right-0.5 transition-transform" />
              </button>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
              <div>
                <p className="text-sm text-foreground">Auto-Correction</p>
                <p className="text-xs text-muted-foreground">Generate corrections for contradicted claims</p>
              </div>
              <button className="h-6 w-11 rounded-full bg-primary relative transition-colors">
                <div className="h-5 w-5 rounded-full bg-primary-foreground absolute top-0.5 right-0.5 transition-transform" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Model Settings */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-glass rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="h-9 w-9 rounded-lg bg-chart-5/10 flex items-center justify-center">
              <Cpu className="h-4 w-4 text-chart-5" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-foreground">Model Configuration</h3>
              <p className="text-xs text-muted-foreground">Choose verification models</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-secondary/50">
              <p className="text-sm text-foreground mb-2">NLI Model</p>
              <select className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground">
                <option>RoBERTa-large-MNLI</option>
                <option>DeBERTa-v3-base-MNLI</option>
                <option>BERT-base-NLI</option>
              </select>
            </div>
            <div className="p-3 rounded-lg bg-secondary/50">
              <p className="text-sm text-foreground mb-2">Embedding Model</p>
              <select className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground">
                <option>all-MiniLM-L6-v2</option>
                <option>text-embedding-3-small</option>
                <option>BGE-large-en</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* API Settings */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-glass rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="h-9 w-9 rounded-lg bg-claim-unverifiable-bg flex items-center justify-center">
              <Globe className="h-4 w-4 text-claim-unverifiable" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-foreground">API Configuration</h3>
              <p className="text-xs text-muted-foreground">Backend connection settings</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-secondary/50">
              <p className="text-sm text-foreground mb-2">API Endpoint</p>
              <input
                type="text"
                defaultValue="http://localhost:8000/api/v1"
                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground"
              />
            </div>
            <div className="p-3 rounded-lg bg-secondary/50">
              <p className="text-sm text-foreground mb-2">API Key</p>
              <input
                type="password"
                defaultValue="sk-xxxxxxxxxxxxxxx"
                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground"
              />
            </div>
          </div>
        </motion.div>

        {/* Save Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex justify-end"
        >
          <button className="px-6 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">
            <Save className="h-4 w-4" />
            Save Settings
          </button>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
