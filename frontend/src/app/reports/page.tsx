"use client";

import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";
import { Loader2, FileText, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

type Scan = {
  id: string;
  name: string;
};

export default function ReportsPage() {
  const [module, setModule] = useState("intrusion");
  const [scan, setScan] = useState("");
  const [scans, setScans] = useState<Scan[]>([]);
  const [loadingScans, setLoadingScans] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [report, setReport] = useState<string | null>(null);

  // 🔹 Fetch scans (mock for now)
  const fetchScans = async (selectedModule: string) => {
    setLoadingScans(true);
    setScan("");
    setReport(null);

    // simulate API
    setTimeout(() => {
      setScans([
        { id: "scan_101", name: "E-commerce App" },
        { id: "scan_102", name: "Banking API" },
        { id: "scan_103", name: "Portfolio Website" },
      ]);
      setLoadingScans(false);
    }, 1000);
  };

  // 🔹 Fetch report
  const fetchReport = async () => {
    if (!scan) return;

    setLoadingReport(true);
    setReport(null);

    setTimeout(() => {
      setReport(`
        🔍 Report Summary:
        Module: ${module}
        Scan ID: ${scan}

        - Vulnerabilities Found: 3
        - Risk Level: Medium
        - Performance Score: 82%

        Recommendations:
        - Fix SQL Injection
        - Optimize API latency
      `);
      setLoadingReport(false);
    }, 1500);
  };

  const handleDownload = () => {
    alert(`Downloading report for ${scan}`);
  };

  return (
    <div className="relative min-h-screen overflow-hidden p-10">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <FlickeringGrid
          className="w-full h-full"
          squareSize={4}
          gridGap={6}
          flickerChance={0.05}
          color="rgb(59, 130, 246)"
          maxOpacity={0.8}
        />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="mb-10 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold gradient-text">
            CognitoForge
          </Link>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4">
              Security <span className="gradient-text">Reports</span>
            </h1>
            <p className="text-muted-foreground">
              Select module and scan to generate report
            </p>
          </div>

          <div className="space-y-6 glass p-8 rounded-lg border border-white/10">
            {/* MODULE SELECT */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Select Module
              </label>
              <select
                value={module}
                onChange={(e) => {
                  setModule(e.target.value);
                  fetchScans(e.target.value);
                }}
                className="w-full px-4 py-3 bg-background/60 border border-border rounded-lg"
              >
                <option value="intrusion">Intrusion Test</option>
                <option value="performance">Performance Test</option>
                <option value="vulnerability">Vulnerability Scanner</option>
              </select>
            </div>

            {/* SCAN SELECT */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Select Scan (ID / Project)
              </label>

              {loadingScans ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Fetching scans...
                </div>
              ) : (
                <select
                  value={scan}
                  onChange={(e) => setScan(e.target.value)}
                  className="w-full px-4 py-3 bg-background/60 border border-border rounded-lg"
                >
                  <option value="">Select a scan</option>
                  {scans.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.id})
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* GENERATE REPORT */}
            <Button
              variant="purple"
              className="w-full"
              onClick={fetchReport}
              disabled={!scan || loadingReport}
            >
              {loadingReport ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Report...
                </>
              ) : (
                "Generate Report"
              )}
            </Button>

            {/* REPORT PREVIEW */}
            {report && (
              <div className="mt-4 p-4 rounded-lg border border-border/40 bg-background/40">
                <div className="flex items-center gap-3 mb-3">
                  <FileText className="h-5 w-5 text-green-500" />
                  <h3 className="font-semibold">Report Preview</h3>
                </div>

                <pre className="text-sm whitespace-pre-wrap text-muted-foreground">
                  {report}
                </pre>

                <Button
                  variant="purple"
                  className="w-full mt-4"
                  onClick={handleDownload}
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download Report
                </Button>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
