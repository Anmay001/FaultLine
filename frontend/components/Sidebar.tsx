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
  Check,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "New Analysis", href: "/", icon: Sparkles },
  { name: "All Repositories", href: "/#repositories", icon: GitFork },
];

const MODULE_LIST = [
  { name: "Structure & Topography", desc: "Manifests & directory layouts", icon: GitFork, status: "complete" },
  { name: "Code Quality & Complexity", desc: "AST & maintainability hotspots", icon: Cpu, status: "complete" },
  { name: "Test Suite Health", desc: "Test coverage & safety gaps", icon: CheckCircle2, status: "complete" },
  { name: "Dependencies & CVEs", desc: "Outdated & unpinned packages", icon: ShieldAlert, status: "complete" },
  { name: "Velocity & Churn", desc: "Commit hotspots & file volatility", icon: History, status: "complete" },
  { name: "Documentation Integrity", desc: "Readme & doc accuracy", icon: BookOpen, status: "complete" },
  { name: "Modular Architecture", desc: "Coupling & circular imports", icon: Layers, status: "complete" },
  { name: "Compound Risk Scoring", desc: "Multi-signal correlation", icon: Sparkles, status: "complete" },
  { name: "Evidence Verification", desc: "Automated proof checks", icon: Check, status: "complete" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 hidden md:flex flex-col border-r border-zinc-800/80 bg-black/60 p-4 space-y-6" role="navigation" aria-label="Analysis modules">
      {/* Navigation Links */}
      <nav className="space-y-1" aria-label="Platform">
        <p className="px-3 text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">
          Platform
        </p>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href === "/#repositories" && pathname === "/");
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "relative flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-[background-color,color,box-shadow] duration-200 focus-visible-ring overflow-hidden group",
                isActive
                  ? "bg-white text-black font-semibold shadow-sm before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-900"
              )}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              <span className="truncate">{item.name}</span>
              {isActive && (
                <ChevronRight className="w-3.5 h-3.5 ml-auto text-black/40" aria-hidden="true" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Analysis Capabilities Overview */}
      <section className="space-y-2 pt-2 border-t border-zinc-800/60" aria-labelledby="modules-heading">
        <div className="flex items-center justify-between px-3">
          <h2 id="modules-heading" className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">
            Analysis Modules
          </h2>
          <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800 font-mono">
            9 Active
          </span>
        </div>

        <div className="space-y-1.5 overflow-y-auto max-h-[calc(100vh-280px)] pr-1">
          {MODULE_LIST.map((module, idx) => {
            const Icon = module.icon;
            return (
              <div
                key={module.name}
                className="relative p-2.5 rounded-xl glass-card text-xs flex flex-col gap-1.5 transition-[border-color,background-color,box-shadow] hover:border-zinc-500/30 group"
                style={{ transitionDelay: `${idx * 20}ms` }}
              >
                <div className="flex items-center gap-2">
                  <div className="relative flex items-center justify-center w-7 h-7 rounded-lg bg-zinc-900/50 border border-zinc-700/50 group-hover:border-zinc-500/50 transition-colors">
                    <Icon className="w-3.5 h-3.5 text-zinc-300 group-hover:text-white transition-colors" aria-hidden="true" />
                    {module.status === "complete" && (
                      <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-white flex items-center justify-center">
                        <Check className="w-2.5 h-2.5 text-black" aria-hidden="true" />
                      </span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="font-semibold text-zinc-100 truncate block">{module.name}</span>
                    <span className="text-[10px] text-zinc-500 font-mono truncate block">{module.desc}</span>
                  </div>
                </div>
                <div className="h-0.5 bg-gradient-to-r from-zinc-700/50 via-zinc-700/20 to-transparent rounded-full overflow-hidden" aria-hidden="true">
                  <div className="h-full w-full bg-gradient-to-r from-white/30 to-transparent" />
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </aside>
  );
}
