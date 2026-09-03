"use client";

import React, { useState } from "react";
import { Finding, Evidence } from "@/types";
import { getSeverityBadge } from "@/lib/utils";
import {
  ShieldCheck,
  ShieldAlert,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  FileCode,
  GitCommit,
  FlaskConical,
  Package,
  Layers,
  FileText,
  Sparkles,
  ExternalLink,
} from "lucide-react";

interface RiskCardProps {
  finding: Finding;
  onInspectFile?: (filePath: string) => void;
}

const CATEGORY_ICONS = {
  CODE: FileCode,
  GIT: GitCommit,
  TEST: FlaskConical,
  DEPENDENCY: Package,
  ARCHITECTURE: Layers,
  DOCUMENTATION: FileText,
  COMPOUNDED: Sparkles,
};

export default function RiskCard({ finding, onInspectFile }: RiskCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const sevBadge = getSeverityBadge(finding.severity);

  const CategoryIcon = CATEGORY_ICONS[finding.category] || AlertCircle;

  const isVerified = finding.verification_status === "VERIFIED";
  const isNotVerified = finding.verification_status === "NOT_VERIFIED";

  return (
    <div
      className={`rounded-2xl glass-card transition-[border-color,background-color,box-shadow] duration-300 border ${
        finding.category === "COMPOUNDED"
          ? "border-zinc-500 bg-zinc-900/60 shadow-lg"
          : isVerified
          ? "border-zinc-800 hover:border-zinc-600 bg-zinc-950/80"
          : isNotVerified
          ? "border-zinc-800 bg-black/80"
          : "border-zinc-800 bg-zinc-950/60"
      }`}
    >
      {/* Header / Clickable summary */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setIsExpanded(!isExpanded);
          }
        }}
        className="flex items-start justify-between p-4 cursor-pointer select-none focus-visible-ring rounded-t-2xl"
        tabIndex={0}
        role="button"
        aria-expanded={isExpanded}
        aria-controls={`evidence-${finding.id}`}
      >
        <div className="flex items-start gap-3.5 flex-1 pr-4">
          {/* Category Icon */}
          <div className="p-2.5 rounded-xl border border-zinc-700 bg-zinc-900 text-white flex-shrink-0 mt-0.5" aria-hidden="true">
            <CategoryIcon className="w-4 h-4" />
          </div>

          <div className="flex flex-col gap-1 flex-1">
            {/* Badges Row */}
            <div className="flex flex-wrap items-center gap-2 font-mono">
              <span
                className={`text-[10px] px-2.5 py-0.5 rounded-md border uppercase tracking-wider ${sevBadge.bg}`}
              >
                {sevBadge.label}
              </span>

              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-zinc-900 text-zinc-300 border border-zinc-800">
                {finding.category}
              </span>

              {/* Verification Status Badge */}
              <div
                className={`flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-md border uppercase tracking-wider ${
                  isVerified
                    ? "bg-white text-black border-white shadow-sm font-black"
                    : isNotVerified
                    ? "bg-zinc-950 text-zinc-500 border-zinc-800"
                    : "bg-zinc-900 text-zinc-300 border-zinc-700"
                }`}
              >
                {isVerified ? (
                  <ShieldCheck className="w-3.5 h-3.5 text-black" aria-hidden="true" />
                ) : isNotVerified ? (
                  <ShieldAlert className="w-3.5 h-3.5 text-zinc-500" aria-hidden="true" />
                ) : (
                  <AlertCircle className="w-3.5 h-3.5 text-zinc-300" aria-hidden="true" />
                )}
                <span>{finding.verification_status.replace("_", " ")}</span>
              </div>

              <span className="text-[11px] text-zinc-500 font-mono ml-auto">
                Confidence: {(finding.confidence * 100).toFixed(0)}%
              </span>
            </div>

            {/* Title */}
            <h4 className="font-bold text-sm text-zinc-100 mt-1 leading-snug">
              {finding.finding}
            </h4>

            {/* Verification Note Snippet */}
            {finding.verification_notes && (
              <p className="text-xs text-zinc-400 font-mono bg-zinc-950 px-2.5 py-1 rounded-lg border border-zinc-800 mt-1">
                {finding.verification_notes}
              </p>
            )}
          </div>
        </div>

        {/* Expand/Collapse Button */}
        <div className="p-1 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors mt-1" aria-hidden="true">
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {/* Expanded Evidence Drawer */}
      {isExpanded && (
        <div
          id={`evidence-${finding.id}`}
          className="p-4 pt-2 border-t border-zinc-800 space-y-3 bg-zinc-950/90 rounded-b-2xl animate-in fade-in duration-200"
          role="region"
          aria-label="Verifiable evidence artifacts"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">
              Verifiable Evidence Artifacts ({finding.evidence.length})
            </span>
          </div>

          <div className="space-y-2">
            {finding.evidence.map((ev, idx) => (
              <div
                key={ev.id || idx}
                className="p-3 rounded-xl bg-black border border-zinc-800 text-xs space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-mono text-zinc-200 font-medium">
                    <FileCode className="w-3.5 h-3.5 text-zinc-400" aria-hidden="true" />
                    <span>{ev.file}</span>
                    {ev.line_start !== null && ev.line_start !== undefined && (
                      <span className="text-[11px] text-zinc-500">
                        (L{ev.line_start}
                        {ev.line_end && ev.line_end !== ev.line_start ? `-L${ev.line_end}` : ""})
                      </span>
                    )}
                  </div>

                  {onInspectFile && ev.file !== "." && ev.file !== ".git" && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onInspectFile(ev.file);
                      }}
                      className="flex items-center gap-1 text-[11px] text-zinc-300 hover:text-white font-semibold font-mono focus-visible-ring rounded px-2 py-1"
                    >
                      <span>View File</span>
                      <ExternalLink className="w-3 h-3" aria-hidden="true" />
                    </button>
                  )}
                </div>

                <p className="text-zinc-300 text-[12px] leading-relaxed">{ev.description}</p>

                {ev.snippet && (
                  <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 font-mono text-[11px] text-zinc-300 overflow-x-auto">
                    <pre>{ev.snippet}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
