"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck, GitFork, PlusCircle } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-zinc-800/80 px-6 py-3.5 bg-black/90">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Logo and Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-700 p-0.5 shadow-lg group-hover:border-zinc-400 transition-all duration-300">
            <div className="w-full h-full bg-black rounded-[8px] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white group-hover:scale-110 transition-transform duration-300" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-xl tracking-tight text-white">
              FaultLine
            </span>
            <span className="text-[11px] text-zinc-400 font-medium">Software Risk & Failure Prevention</span>
          </div>
        </Link>

        {/* User Navigation Actions */}
        <div className="flex items-center gap-3 font-mono text-xs">
          <Link
            href="/#repositories"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-900 transition-colors"
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>Repositories</span>
          </Link>

          <Link
            href="/"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold transition-all shadow-sm"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
