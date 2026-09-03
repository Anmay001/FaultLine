"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Layers,
  ArrowRight,
  GitFork,
  Activity,
  CheckCircle2,
  FileCode,
  Lock,
  Sparkles,
  GitBranch,
  Search,
  ChevronRight,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from "lucide-react";
import RepositoryInput from "@/components/RepositoryInput";
import { listAnalyses, listRepositories } from "@/lib/api";
import { AnalysisRun, Repository } from "@/types";
import { getScoreColor } from "@/lib/utils";

const MODULE_PREVIEW = [
  { name: "Structure & Topography", icon: GitBranch, color: "text-white", desc: "Manifests & directory layouts" },
  { name: "Code Quality", icon: BarChart3, color: "text-zinc-300", desc: "AST & maintainability hotspots" },
  { name: "Test Suite Health", icon: CheckCircle, color: "text-zinc-400", desc: "Coverage & safety gaps" },
  { name: "Dependencies & CVEs", icon: AlertTriangle, color: "text-zinc-500", desc: "Outdated & unpinned packages" },
  { name: "Velocity & Churn", icon: GitFork, color: "text-zinc-400", desc: "Commit hotspots & file volatility" },
  { name: "Documentation", icon: FileCode, color: "text-zinc-500", desc: "Readme & doc accuracy" },
  { name: "Modular Architecture", icon: Layers, color: "text-zinc-300", desc: "Coupling & circular imports" },
  { name: "Compound Risk", icon: XCircle, color: "text-zinc-400", desc: "Multi-signal correlation" },
];

export default function HomePage() {
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisRun[]>([]);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listAnalyses(6), listRepositories()])
      .then(([analysesData, reposData]) => {
        setRecentAnalyses(analysesData || []);
        setRepos(reposData || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-16 max-w-6xl mx-auto py-6 md:py-10">
      {/* Hero Section - Modernized */}
      <section aria-labelledby="hero-title" className="relative space-y-8">
        {/* Background decorative elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute top-0 right-1/4 w-[400px] h-[400px] bg-gradient-to-br from-white/5 via-transparent to-transparent rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-1/4 w-[300px] h-[300px] bg-gradient-to-tr from-white/3 via-transparent to-transparent rounded-full blur-3xl" />
        </div>

        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-zinc-900/80 border border-zinc-700 text-zinc-300 text-xs font-bold uppercase tracking-wider shadow-lg font-mono backdrop-blur" aria-hidden="true">
          <Sparkles className="w-3.5 h-3.5 text-white" aria-hidden="true" />
          <span>Automated Code Risk & Health Detection</span>
        </div>

        {/* Headline */}
        <h1 id="hero-title" className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-[1.05] text-white text-wrap-balance">
          Detect Software Project Risks
          <br />
          <span className="bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
            Before Production
          </span>
        </h1>

        {/* Subheadline */}
        <p className="text-zinc-400 text-base md:text-lg max-w-2xl mx-auto leading-relaxed text-wrap-pretty">
          FaultLine analyzes repositories to detect architectural risks, test gaps,
          outdated dependencies, and velocity bottlenecks with automated evidence
          verification.
        </p>

        {/* Visual Module Preview - shows what the platform analyzes */}
        <div className="relative mt-4" aria-hidden="true">
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-3 lg:gap-4">
            {MODULE_PREVIEW.map((module, idx) => {
              const Icon = module.icon;
              return (
                <div
                  key={module.name}
                  className="group relative flex flex-col items-center gap-1.5 px-3 py-2.5 rounded-2xl glass-card border border-zinc-800/80 hover:border-zinc-500/50 transition-[border-color,background-color,box-shadow] cursor-default"
                  style={{ transitionDelay: `${idx * 50}ms` }}
                >
                  <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-zinc-900/50 border border-zinc-700/50 group-hover:border-zinc-500/50 transition-colors">
                    <Icon className={`w-5 h-5 ${module.color} group-hover:text-white transition-colors`} aria-hidden="true" />
                    {/* Pulse indicator for active modules */}
                    <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-white/20 group-hover:bg-white/40 transition-colors" />
                  </div>
                  <span className="text-[10px] font-medium text-zinc-300 text-center leading-snug max-w-[80px]">{module.name}</span>
                </div>
              );
            })}
          </div>
          {/* Subtle label */}
          <p className="text-[10px] text-zinc-600 font-mono text-center mt-3 uppercase tracking-widest">
            9 Analysis Modules &hellip; Runs in Parallel
          </p>
        </div>

        {/* Value Prop Badges - Enhanced */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2 text-xs font-medium text-zinc-300 font-mono">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card border border-zinc-800">
            <CheckCircle2 className="w-4 h-4 text-white" aria-hidden="true" />
            <span>Verifiable Code Evidence</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card border border-zinc-800">
            <Layers className="w-4 h-4 text-zinc-300" aria-hidden="true" />
            <span>Cross-Domain Risk Scoring</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card border border-zinc-800">
            <Lock className="w-4 h-4 text-zinc-400" aria-hidden="true" />
            <span>Secure & Isolated Analysis</span>
          </div>
        </div>
      </section>

      {/* Main Repository Input Card */}
      <RepositoryInput />

      {/* Recent Analyses Section */}
      <section aria-labelledby="recent-analyses-heading" className="space-y-6 pt-6" id="repositories">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 id="recent-analyses-heading" className="text-xl font-black text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-white" aria-hidden="true" />
              <span>Recent Intelligence Runs</span>
            </h2>
            <p className="text-xs text-zinc-500 font-mono mt-1">Previous audited repositories and score profiles</p>
          </div>

          <span className="text-xs text-zinc-500 font-mono self-start sm:self-center" aria-live="polite">
            {recentAnalyses.length} runs recorded
          </span>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4" aria-label="Loading recent analyses">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-40 rounded-2xl glass-card border border-zinc-800 animate-pulse" aria-hidden="true" />
            ))}
          </div>
        ) : recentAnalyses.length === 0 ? (
          <div className="p-10 rounded-2xl glass-card border border-zinc-800 text-center space-y-3">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-zinc-900 border border-zinc-700 flex items-center justify-center mb-2">
              <Search className="w-8 h-8 text-zinc-500" aria-hidden="true" />
            </div>
            <p className="text-sm text-zinc-400 font-mono">No repository analyses recorded yet.</p>
            <p className="text-xs text-zinc-600 max-w-xs mx-auto">Enter a Git repository URL above to launch your first intelligence audit.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4" role="list" aria-label="Recent analyses">
            {recentAnalyses.map((item) => {
              const scoreInfo = getScoreColor(item.overall_score);
              return (
                <Link
                  key={item.id}
                  href={`/results/${item.id}`}
                  className="p-5 rounded-2xl glass-card border border-zinc-800 hover:border-zinc-500 transition-[border-color,background-color,box-shadow] flex flex-col justify-between space-y-4 group focus-visible-ring"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between font-mono">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                        {item.branch || "main"}
                      </span>
                      <span
                        className={`text-[10px] font-black px-2 py-0.5 rounded-md border uppercase ${scoreInfo.bg} ${scoreInfo.text} ${scoreInfo.border}`}
                      >
                        {scoreInfo.label}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-zinc-400 group-hover:text-white transition-colors" aria-hidden="true" />
                      <h3 className="font-bold text-sm text-zinc-100 group-hover:text-white truncate">
                        Analysis #{item.id.slice(0, 8)}
                      </h3>
                    </div>

                    {item.summary && (
                      <p className="text-xs text-zinc-400 line-clamp-2 leading-relaxed">
                        {item.summary}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-zinc-800/80 text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-zinc-500">Score:</span>
                      <span className="font-black text-sm text-white">
                        {item.overall_score !== null && item.overall_score !== undefined
                          ? item.overall_score.toFixed(1)
                          : "Pending"}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-zinc-300 group-hover:text-white text-xs font-semibold group-hover:translate-x-1 transition-transform">
                      <span>View Report</span>
                      <ChevronRight className="w-3.5 h-3.5" aria-hidden="true" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
