"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck, GitFork, Github, Twitter, Mail, ExternalLink } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-zinc-800/80 bg-black/60 px-6 py-8 md:py-12" role="contentinfo">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12">
          {/* Brand */}
          <div className="md:col-span-1 lg:col-span-2 space-y-4">
            <Link href="/" className="flex items-center gap-3 group focus-visible-ring rounded-xl" aria-label="FaultLine home">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-700 p-0.5 shadow-lg group-hover:border-zinc-400 transition-[border-color,box-shadow] duration-300" aria-hidden="true">
                <div className="w-full h-full bg-black rounded-[8px] flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-white group-hover:scale-110 transition-transform duration-300" aria-hidden="true" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-xl tracking-tight text-white">
                  FaultLine
                </span>
                <span className="text-[11px] text-zinc-400 font-medium">Software Risk & Failure Prevention</span>
              </div>
            </Link>
            <p className="text-zinc-400 text-sm max-w-xs leading-relaxed">
              Autonomous agentic software project failure intelligence platform powered by deterministic AST,
              static analysis, test inspection, and ground-truth verification.
            </p>
            <div className="flex items-center gap-4 pt-2">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="p-2 rounded-xl bg-zinc-900 border border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-500 transition-[color,border-color] focus-visible-ring" aria-label="GitHub">
                <Github className="w-5 h-5" aria-hidden="true" />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="p-2 rounded-xl bg-zinc-900 border border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-500 transition-[color,border-color] focus-visible-ring" aria-label="Twitter">
                <Twitter className="w-5 h-5" aria-hidden="true" />
              </a>
              <a href="mailto:support@faultline.dev" className="p-2 rounded-xl bg-zinc-900 border border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-500 transition-[color,border-color] focus-visible-ring" aria-label="Email">
                <Mail className="w-5 h-5" aria-hidden="true" />
              </a>
            </div>
          </div>

          {/* Platform */}
          <div className="space-y-4">
            <h4 className="font-bold text-zinc-100">Platform</h4>
            <nav aria-label="Platform links">
              <ul className="space-y-2">
                <li><Link href="/" className="text-zinc-400 hover:text-white text-sm transition-colors font-mono focus-visible-ring">New Analysis</Link></li>
                <li><Link href="/#repositories" className="text-zinc-400 hover:text-white text-sm transition-colors font-mono focus-visible-ring">Repositories</Link></li>
                <li><Link href="/#repositories" className="text-zinc-400 hover:text-white text-sm transition-colors font-mono focus-visible-ring">Recent Runs</Link></li>
                <li><Link href="#" className="text-zinc-400 hover:text-white text-sm transition-colors font-mono focus-visible-ring">Documentation</Link></li>
              </ul>
            </nav>
          </div>

          {/* Analysis Modules */}
          <div className="space-y-4">
            <h4 className="font-bold text-zinc-100">Analysis Modules</h4>
            <nav aria-label="Analysis modules">
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Structure & Topography</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Code Quality & Complexity</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Test Suite Health</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Dependencies & CVEs</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Velocity & Churn</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Documentation Integrity</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Modular Architecture</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Compound Risk Scoring</span></li>
                <li className="flex items-center gap-2 text-zinc-400"><ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" /><span>Evidence Verification</span></li>
              </ul>
            </nav>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-zinc-800/80 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-zinc-500 font-mono">
            &copy; {new Date().getFullYear()} FaultLine. All rights reserved.
          </p>
          <div className="flex items-center gap-4 text-xs text-zinc-500 font-mono">
            <Link href="#" className="hover:text-zinc-300 transition-colors focus-visible-ring">Privacy</Link>
            <Link href="#" className="hover:text-zinc-300 transition-colors focus-visible-ring">Terms</Link>
            <Link href="#" className="hover:text-zinc-300 transition-colors focus-visible-ring">Security</Link>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:text-zinc-300 transition-colors focus-visible-ring">
              <ExternalLink className="w-3 h-3" aria-hidden="true" />
              <span>Open Source</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}