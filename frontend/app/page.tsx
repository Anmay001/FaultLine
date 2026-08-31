"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Zap,
  Layers,
  ArrowRight,
  GitFork,
  Activity,
  CheckCircle2,
  FileCode,
  Lock,
  Sparkles,
} from "lucide-react";
import RepositoryInput from "@/components/RepositoryInput";
import { listAnalyses, listRepositories } from "@/lib/api";
import { AnalysisRun, Repository } from "@/types";
import { getScoreColor } from "@/lib/utils";

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
    <div className="space-y-12 max-w-6xl mx-auto py-4">
      {/* Hero Section */}
      <div className="text-center space-y-5 relative">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs font-bold uppercase tracking-wider shadow-lg font-mono">
          <Sparkles className="w-3.5 h-3.5 text-white" />
          <span>Automated Code Risk & Health Detection</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black tracking-tight leading-tight text-white">
          Detect Software Project Risks{" "}
          <span className="bg-gradient-to-r from-white via-zinc-300 to-zinc-500 bg-clip-text text-transparent">
            Before Production
          </span>
        </h1>

        <p className="text-zinc-400 text-base md:text-lg max-w-2xl mx-auto leading-relaxed">
          FaultLine analyzes repositories to detect architectural risks, test gaps,
          outdated dependencies, and velocity bottlenecks with automated evidence verification.
        </p>

        {/* Value Prop Badges */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2 text-xs font-medium text-zinc-300 font-mono">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card border border-zinc-800">
            <CheckCircle2 className="w-4 h-4 text-white" />
            <span>Verifiable Code Evidence</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card border border-zinc-800">
            <Layers className="w-4 h-4 text-zinc-300" />
            <span>Cross-Domain Risk Scoring</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass-card border border-zinc-800">
            <Lock className="w-4 h-4 text-zinc-400" />
            <span>Secure & Isolated Analysis</span>
          </div>
        </div>
      </div>

      {/* Main Repository Input Card */}
      <RepositoryInput />

      {/* Recent Analyses Section */}
      <div className="space-y-6 pt-6" id="repositories">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-black text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-white" />
              <span>Recent Intelligence Runs</span>
            </h2>
            <p className="text-xs text-zinc-500 font-mono">Previous audited repositories and score profiles</p>
          </div>

          <span className="text-xs text-zinc-500 font-mono">
            {recentAnalyses.length} runs recorded
          </span>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-36 rounded-2xl glass-card border border-zinc-800 animate-pulse" />
            ))}
          </div>
        ) : recentAnalyses.length === 0 ? (
          <div className="p-8 rounded-2xl glass-card border border-zinc-800 text-center space-y-2">
            <p className="text-sm text-zinc-400 font-mono">No repository analyses recorded yet.</p>
            <p className="text-xs text-zinc-600">Enter a Git repository URL above to launch your first intelligence audit.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentAnalyses.map((item) => {
              const scoreInfo = getScoreColor(item.overall_score);
              return (
                <Link
                  key={item.id}
                  href={`/results/${item.id}`}
                  className="p-5 rounded-2xl glass-card border border-zinc-800 hover:border-zinc-500 transition-all flex flex-col justify-between space-y-4 group"
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
                      <FileCode className="w-4 h-4 text-zinc-400 group-hover:text-white transition-colors" />
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
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
