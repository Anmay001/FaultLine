"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldAlert,
  GitFork,
  CheckCircle2,
  Cpu,
  Layers,
  History,
  BookOpen,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "New Analysis", href: "/", icon: Sparkles },
  { name: "All Repositories", href: "/#repositories", icon: GitFork },
];

const MODULE_LIST = [
  { name: "Structure & Topography", desc: "Manifests & directory layouts", color: "bg-white" },
  { name: "Code Quality & Complexity", desc: "AST & maintainability hotspots", color: "bg-zinc-200" },
  { name: "Test Suite Health", desc: "Test coverage & safety gaps", color: "bg-zinc-300" },
  { name: "Dependencies & CVEs", desc: "Outdated & unpinned packages", color: "bg-zinc-400" },
  { name: "Velocity & Churn", desc: "Commit hotspots & file volatility", color: "bg-zinc-300" },
  { name: "Documentation Integrity", desc: "Readme & doc accuracy", color: "bg-zinc-400" },
  { name: "Modular Architecture", desc: "Coupling & circular imports", color: "bg-zinc-200" },
  { name: "Compound Risk Scoring", desc: "Multi-signal correlation", color: "bg-white" },
  { name: "Evidence Verification", desc: "Automated proof checks", color: "bg-zinc-100" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 hidden md:flex flex-col border-r border-zinc-800/80 bg-black/60 p-4 space-y-6">
      {/* Navigation Links */}
      <div className="space-y-1">
        <p className="px-3 text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">
          Platform
        </p>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-white text-black font-semibold shadow-sm"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-900"
              )}
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Analysis Capabilities Overview */}
      <div className="space-y-2 pt-2 border-t border-zinc-800/60">
        <div className="flex items-center justify-between px-3">
          <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">
            Analysis Modules
          </p>
          <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800 font-mono">
            9 Active
          </span>
        </div>

        <div className="space-y-1.5 overflow-y-auto max-h-[calc(100vh-280px)] pr-1">
          {MODULE_LIST.map((module) => (
            <div
              key={module.name}
              className="p-2.5 rounded-xl glass-card text-xs flex flex-col gap-0.5"
            >
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${module.color}`} />
                <span className="font-semibold text-zinc-200">{module.name}</span>
              </div>
              <span className="text-[11px] text-zinc-500 pl-3.5 font-mono">{module.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
