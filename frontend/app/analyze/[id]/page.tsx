"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ShieldCheck,
  Cpu,
  Layers,
  Sparkles,
  GitBranch,
  Terminal,
  CheckCircle2,
  Clock,
  AlertCircle,
} from "lucide-react";
import { getAnalysis } from "@/lib/api";
import { AnalysisRun } from "@/types";

const PIPELINE_STEPS = [
  { id: 1, name: "Cloning Repository", desc: "Cloning branch and repository structure" },
  { id: 2, name: "Code & Quality Inspection", desc: "Inspecting source code, test suite, and dependencies" },
  { id: 3, name: "Correlating Risk Signals", desc: "Identifying compound hotspots across quality dimensions" },
  { id: 4, name: "Verifying Code Evidence", desc: "Validating file paths, line ranges, and proof snippets" },
  { id: 5, name: "Compiling Health Report", desc: "Calculating weighted category scores and report summary" },
];

export default function AnalyzeProgressPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const [analysis, setAnalysis] = useState<AnalysisRun | null>(null);
  const [currentStep, setCurrentStep] = useState(2);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) return;

    let interval: NodeJS.Timeout;

    const poll = async () => {
      try {
        const data = await getAnalysis(analysisId);
        setAnalysis(data);

        if (data.status === "COMPLETED") {
          setCurrentStep(5);
          setTimeout(() => {
            router.push(`/results/${analysisId}`);
          }, 1200);
        } else if (data.status === "FAILED") {
          setError(data.error_message || "Analysis failed unexpectedly.");
        } else if (data.status === "RUNNING") {
          setCurrentStep((prev) => (prev < 4 ? prev + 1 : prev));
        }
      } catch (err: any) {
        setError(err.message || "Failed to communicate with analysis service.");
      }
    };

    poll();
    interval = setInterval(poll, 2000);

    return () => clearInterval(interval);
  }, [analysisId, router]);

  return (
    <div className="max-w-4xl mx-auto py-12 space-y-8">
      {/* Header Card */}
      <div className="p-8 rounded-3xl glass-panel border border-zinc-800 shadow-2xl text-center space-y-4 glow-gradient bg-black">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-700 text-white animate-pulse">
          <Cpu className="w-7 h-7" />
        </div>

        <div className="space-y-1">
          <h2 className="text-2xl md:text-3xl font-black text-white">
            Analyzing Repository
          </h2>
          <p className="text-sm text-zinc-400 font-mono">
            Analysis ID: <span className="text-zinc-200 font-bold">{analysisId}</span>
          </p>
        </div>

        {/* Telemetry pill */}
        <div className="flex items-center justify-center gap-4 text-xs font-mono text-zinc-400 pt-2">
          {analysis?.branch && (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300">
              <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
              <span>{analysis.branch}</span>
            </div>
          )}
          {analysis?.commit_hash && (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300">
              <Terminal className="w-3.5 h-3.5 text-white" />
              <span>{analysis.commit_hash.slice(0, 8)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 text-zinc-300 text-sm flex items-center gap-3 font-mono">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-white" />
          <span>{error}</span>
        </div>
      )}

      {/* Execution Pipeline Stepper */}
      <div className="p-6 rounded-3xl glass-card border border-zinc-800 space-y-4 bg-zinc-950/80">
        <h3 className="font-bold text-xs text-zinc-400 uppercase tracking-widest px-2 font-mono">
          Analysis Pipeline
        </h3>

        <div className="space-y-3 font-mono">
          {PIPELINE_STEPS.map((step) => {
            const isCompleted = step.id < currentStep || analysis?.status === "COMPLETED";
            const isCurrent = step.id === currentStep && analysis?.status !== "COMPLETED";

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between p-4 rounded-2xl border transition-all duration-300 ${
                  isCompleted
                    ? "bg-zinc-900/90 border-zinc-700 text-zinc-200"
                    : isCurrent
                    ? "bg-white text-black border-white shadow-xl"
                    : "bg-black/60 border-zinc-800/80 text-zinc-600"
                }`}
              >
                <div className="flex items-center gap-3.5">
                  <div
                    className={`w-8 h-8 rounded-xl flex items-center justify-center font-black text-xs ${
                      isCompleted
                        ? "bg-zinc-800 text-white border border-zinc-700"
                        : isCurrent
                        ? "bg-black text-white"
                        : "bg-zinc-900 text-zinc-600 border border-zinc-800"
                    }`}
                  >
                    {isCompleted ? <CheckCircle2 className="w-4 h-4 text-white" /> : step.id}
                  </div>

                  <div>
                    <h4 className={`font-bold text-sm leading-tight ${isCurrent ? "text-black" : "text-zinc-100"}`}>
                      {step.name}
                    </h4>
                    <p className={`text-xs mt-0.5 ${isCurrent ? "text-zinc-700" : "text-zinc-400"}`}>
                      {step.desc}
                    </p>
                  </div>
                </div>

                <div>
                  {isCompleted ? (
                    <span className="text-xs font-bold text-zinc-300 font-mono">COMPLETE</span>
                  ) : isCurrent ? (
                    <div className="flex items-center gap-2 text-xs font-black text-black">
                      <div className="w-3 h-3 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                      <span>PROCESSING</span>
                    </div>
                  ) : (
                    <span className="text-xs text-zinc-600 font-mono">QUEUED</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
