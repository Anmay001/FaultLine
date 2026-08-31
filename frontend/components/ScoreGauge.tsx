"use client";

import React from "react";
import { getScoreColor } from "@/lib/utils";
import { ShieldCheck, ShieldAlert, AlertTriangle } from "lucide-react";

interface ScoreGaugeProps {
  score?: number | null;
  verifiedCount?: number;
  refutedCount?: number;
}

export default function ScoreGauge({
  score = 0,
  verifiedCount = 0,
  refutedCount = 0,
}: ScoreGaugeProps) {
  const safeScore = score ?? 0;
  const colors = getScoreColor(safeScore);
  const strokeDashoffset = 440 - (440 * safeScore) / 100;

  return (
    <div className="relative flex flex-col items-center justify-center p-6 rounded-2xl glass-card border border-zinc-800 shadow-2xl overflow-hidden group">
      {/* Background glow */}
      <div className="absolute inset-0 opacity-15 transition-opacity duration-500 group-hover:opacity-25 glow-gradient" />

      <div className="relative flex items-center justify-center w-48 h-48">
        {/* SVG Circular Progress */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke="currentColor"
            strokeWidth="10"
            className="text-zinc-800 fill-transparent"
          />
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke="currentColor"
            strokeWidth="10"
            strokeDasharray="440"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${colors.text} fill-transparent transition-all duration-1000 ease-out`}
          />
        </svg>

        {/* Inner Content */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-black tracking-tight text-white font-mono">
            {safeScore.toFixed(1)}
          </span>
          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mt-0.5 font-mono">
            Health Score
          </span>
        </div>
      </div>

      {/* Severity Badge */}
      <div className="mt-4 flex flex-col items-center gap-2">
        <span
          className={`px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase border ${colors.bg} ${colors.text} ${colors.border}`}
        >
          {colors.label}
        </span>

        {/* Verification Summary Chips */}
        <div className="flex items-center gap-2 mt-2 font-mono">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-700 text-[11px] font-semibold text-zinc-200">
            <ShieldCheck className="w-3.5 h-3.5 text-white" />
            <span>{verifiedCount} Verified Proofs</span>
          </div>
          {refutedCount > 0 && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-950 border border-zinc-800 text-[11px] font-semibold text-zinc-400">
              <ShieldAlert className="w-3.5 h-3.5 text-zinc-400" />
              <span>{refutedCount} Refuted Claims</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
