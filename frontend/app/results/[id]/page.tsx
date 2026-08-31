"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck,
  ShieldAlert,
  Terminal,
  GitBranch,
  Filter,
  RefreshCw,
  FolderTree,
  AlertTriangle,
  ArrowLeft,
  Sparkles,
  Layers,
  FileCheck,
} from "lucide-react";
import { getAnalysis } from "@/lib/api";
import { AnalysisRun, Finding, RiskCategory, RiskSeverity, VerificationStatus } from "@/types";
import ScoreGauge from "@/components/ScoreGauge";
import RadarBreakdown from "@/components/RadarBreakdown";
import RiskCard from "@/components/RiskCard";
import SandboxInspector from "@/components/SandboxInspector";

export default function ResultsPage() {
  const params = useParams();
  const analysisId = params.id as string;

  const [analysis, setAnalysis] = useState<AnalysisRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");

  // Sandbox inspector state
  const [inspectModalOpen, setInspectModalOpen] = useState(false);
  const [inspectInitialFile, setInspectInitialFile] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) return;

    setLoading(true);
    getAnalysis(analysisId)
      .then((data) => setAnalysis(data))
      .catch((err) => setError(err.message || "Failed to load analysis"))
      .finally(() => setLoading(false));
  }, [analysisId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-10 h-10 border-4 border-zinc-800 border-t-white rounded-full animate-spin" />
        <p className="text-sm font-mono text-zinc-400">Loading verified intelligence report...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center space-y-4 font-mono">
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 text-zinc-300 text-sm">
          {error || "Analysis not found"}
        </div>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black text-xs font-bold shadow-md hover:bg-zinc-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>
      </div>
    );
  }

  // Filter findings
  const findings = analysis.findings || [];
  const filteredFindings = findings.filter((f) => {
    if (selectedCategory !== "ALL" && f.category !== selectedCategory) return false;
    if (selectedSeverity !== "ALL" && f.severity !== selectedSeverity) return false;
    if (selectedStatus !== "ALL" && f.verification_status !== selectedStatus) return false;
    return true;
  });

  const verifiedCount = findings.filter((f) => f.verification_status === "VERIFIED").length;
  const refutedCount = findings.filter((f) => f.verification_status === "NOT_VERIFIED").length;
  const compoundedCount = findings.filter((f) => f.category === "COMPOUNDED").length;

  const handleInspectFile = (filePath: string) => {
    setInspectInitialFile(filePath);
    setInspectModalOpen(true);
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-4">
      {/* Top Breadcrumb & Metadata Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-zinc-800">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 font-mono">
            <Link
              href="/"
              className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Analyses</span>
            </Link>
            <span className="text-zinc-700">/</span>
            <span className="text-xs font-mono text-zinc-300 font-bold">#{analysis.id.slice(0, 8)}</span>
          </div>

          <h1 className="text-2xl md:text-3xl font-black text-white flex items-center gap-3">
            <span>Repository Health & Risk Report</span>
            {compoundedCount > 0 && (
              <span className="text-xs font-extrabold px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-700 text-zinc-200 uppercase tracking-wide font-mono">
                {compoundedCount} Compounded Risks
              </span>
            )}
          </h1>

          <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-zinc-400 pt-1">
            {analysis.branch && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-950 border border-zinc-800 text-zinc-300">
                <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
                <span>{analysis.branch}</span>
              </div>
            )}
            {analysis.commit_hash && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-950 border border-zinc-800 text-zinc-300">
                <Terminal className="w-3.5 h-3.5 text-zinc-400" />
                <span>{analysis.commit_hash.slice(0, 8)}</span>
              </div>
            )}
            <span className="text-zinc-700">•</span>
            <span>{new Date(analysis.created_at).toLocaleString()}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 font-mono">
          <button
            onClick={() => {
              setInspectInitialFile(null);
              setInspectModalOpen(true);
            }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-white text-xs font-bold transition-all shadow-md"
          >
            <FolderTree className="w-4 h-4 text-zinc-300" />
            <span>Explore Files</span>
          </button>
        </div>
      </div>

      {/* Top Overview Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Overall Health Score & Summary */}
        <div className="lg:col-span-5 flex flex-col space-y-6">
          <ScoreGauge
            score={analysis.overall_score}
            verifiedCount={verifiedCount}
            refutedCount={refutedCount}
          />

          {/* Executive Summary Card */}
          {analysis.summary && (
            <div className="p-5 rounded-2xl glass-card border border-zinc-800 space-y-2.5">
              <div className="flex items-center gap-2 text-xs font-bold text-zinc-300 uppercase tracking-widest font-mono">
                <Sparkles className="w-3.5 h-3.5 text-white" />
                <span>Executive Synthesis</span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed font-sans">
                {analysis.summary}
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Category Radar & Bar Breakdown */}
        <div className="lg:col-span-7">
          <RadarBreakdown
            codeScore={analysis.code_risk_score}
            testScore={analysis.test_risk_score}
            gitScore={analysis.git_risk_score}
            depScore={analysis.dependency_risk_score}
            archScore={analysis.architecture_risk_score}
            docScore={analysis.documentation_risk_score}
          />
        </div>
      </div>

      {/* Findings Section */}
      <div className="space-y-6 pt-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-black text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-white" />
              <span>Verified Risk Findings</span>
            </h2>
            <p className="text-xs text-zinc-500 font-mono">
              Showing {filteredFindings.length} of {findings.length} findings
            </p>
          </div>

          {/* Filters Bar */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            >
              <option value="ALL">All Categories</option>
              <option value="COMPOUNDED">Compounded Hotspots</option>
              <option value="CODE">Code Quality</option>
              <option value="TEST">Test Suite</option>
              <option value="GIT">Git Velocity</option>
              <option value="DEPENDENCY">Dependencies</option>
              <option value="ARCHITECTURE">Architecture</option>
              <option value="DOCUMENTATION">Documentation</option>
            </select>

            {/* Severity Filter */}
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            {/* Verification Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            >
              <option value="ALL">All Statuses</option>
              <option value="VERIFIED">Verified Proofs</option>
              <option value="NOT_VERIFIED">Refuted Claims</option>
              <option value="INSUFFICIENT_EVIDENCE">Insufficient Evidence</option>
            </select>
          </div>
        </div>

        {/* Findings List */}
        {filteredFindings.length === 0 ? (
          <div className="p-8 rounded-2xl glass-card border border-zinc-800 text-center space-y-2">
            <ShieldCheck className="w-8 h-8 text-white mx-auto" />
            <h4 className="text-sm font-bold text-zinc-300">No findings matching active filter</h4>
            <p className="text-xs text-zinc-500 font-mono">
              Clear or change your filters above to inspect all findings.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredFindings.map((finding) => (
              <RiskCard
                key={finding.id}
                finding={finding}
                onInspectFile={handleInspectFile}
              />
            ))}
          </div>
        )}
      </div>

      {/* Sandbox File Inspector Modal */}
      {inspectModalOpen && (
        <SandboxInspector
          analysisId={analysis.id}
          initialFile={inspectInitialFile}
          onClose={() => setInspectModalOpen(false)}
        />
      )}
    </div>
  );
}
