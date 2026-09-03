"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  GitBranch,
  Github,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { triggerAnalysis } from "@/lib/api";

const SAMPLE_REPOSITORIES = [
  { name: "FastAPI", url: "https://github.com/fastapi/fastapi", tag: "Python" },
  { name: "Flask", url: "https://github.com/pallets/flask", tag: "Python" },
  { name: "Express", url: "https://github.com/expressjs/express", tag: "Node" },
  { name: "Axios", url: "https://github.com/axios/axios", tag: "TypeScript" },
];

export default function RepositoryInput() {
  const router = useRouter();
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [urlError, setUrlError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;

    // Basic URL validation
    try {
      new URL(repoUrl.trim());
      if (!repoUrl.includes("github.com")) {
        setUrlError("Only GitHub repositories are supported");
        return;
      }
    } catch {
      setUrlError("Enter a valid URL");
      return;
    }

    setUrlError(null);
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await triggerAnalysis({
        repo_url: repoUrl.trim(),
        branch: branch.trim() || undefined,
      });

      router.push(`/analyze/${result.id}`);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to trigger analysis. Please check the backend.");
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto rounded-3xl glass-panel p-8 border border-zinc-800/90 shadow-2xl overflow-hidden glow-gradient" role="region" aria-labelledby="repo-input-heading">
      {/* Header Accent */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs font-bold uppercase tracking-wider font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-white" aria-hidden="true" />
          <span id="repo-input-heading">Repository Security & Risk Analysis</span>
        </div>

        <div className="text-xs text-zinc-400 font-mono">
          Automated Code & Test Verification
        </div>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* URL Input */}
          <div className="relative flex-1 w-full">
            <label htmlFor="repo-url" className="sr-only">
              Repository URL
            </label>
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-zinc-500" aria-hidden="true">
              <Github className="w-5 h-5" />
            </div>
            <input
              type="url"
              id="repo-url"
              required
              value={repoUrl}
              onChange={(e) => {
                setRepoUrl(e.target.value);
                setUrlError(null);
              }}
              placeholder="https://github.com/owner/repository…"
              autoComplete="url"
              spellCheck={false}
              className="w-full pl-12 pr-4 py-4 rounded-2xl bg-zinc-950 border border-zinc-800 text-white placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-white font-mono text-sm transition-[border-color,box-shadow,background-color] shadow-inner focus-visible-ring"
              aria-describedby={urlError ? "repo-url-error" : "repo-url-hint"}
              aria-invalid={urlError ? "true" : "false"}
            />
            {urlError ? (
              <span id="repo-url-error" className="sr-only">{urlError}</span>
            ) : (
              <span id="repo-url-hint" className="sr-only">Enter a GitHub repository URL</span>
            )}
          </div>

          {/* Branch Input */}
          <div className="relative w-full md:w-52">
            <label htmlFor="branch" className="sr-only">
              Branch (optional)
            </label>
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500" aria-hidden="true">
              <GitBranch className="w-4 h-4" />
            </div>
            <input
              type="text"
              id="branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="default branch…"
              autoComplete="off"
              spellCheck={false}
              className="w-full pl-10 pr-3 py-4 rounded-2xl bg-zinc-950 border border-zinc-800 text-white placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-white font-mono text-sm transition-[border-color,box-shadow,background-color] focus-visible-ring"
              aria-describedby="branch-hint"
            />
            <span id="branch-hint" className="sr-only">Optional branch name, defaults to repository default</span>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !repoUrl.trim()}
            className="w-full md:w-auto px-8 py-4 rounded-2xl bg-white hover:bg-zinc-200 text-black font-black text-sm tracking-wide flex items-center justify-center gap-2 shadow-xl hover:shadow-2xl disabled:opacity-30 disabled:cursor-not-allowed transition-[background-color,box-shadow,transform] duration-200 active:scale-95 focus-visible-ring"
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <span className="sr-only">Launching sandbox analysis...</span>
                <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" aria-hidden="true" />
                <span>Launching Sandbox&hellip;</span>
              </>
            ) : (
              <>
                <span>Run FaultLine</span>
                <ArrowRight className="w-4 h-4" aria-hidden="true" />
              </>
            )}
          </button>
        </div>

        {/* Inline URL Error */}
        {urlError && (
          <div
            className="p-3 rounded-xl bg-zinc-950 border border-zinc-700 text-zinc-200 text-xs font-medium flex items-center gap-2 font-mono"
            role="alert"
            aria-live="polite"
          >
            <span>{urlError}</span>
          </div>
        )}

        {/* Submit Error Alert */}
        {errorMessage && (
          <div
            className="p-3 rounded-xl bg-zinc-950 border border-zinc-700 text-zinc-200 text-xs font-medium flex items-center gap-2 font-mono"
            role="alert"
            aria-live="polite"
          >
            <span>{errorMessage}</span>
          </div>
        )}
      </form>

      {/* Quick Sample Repositories */}
      <div className="mt-6 pt-5 border-t border-zinc-800/80 flex flex-wrap items-center gap-2.5 text-xs">
        <span className="text-zinc-500 font-mono">Sample Targets:</span>
        {SAMPLE_REPOSITORIES.map((repo) => (
          <button
            key={repo.name}
            type="button"
            onClick={() => {
              setRepoUrl(repo.url);
              setBranch("");
              setUrlError(null);
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-950 hover:bg-zinc-900 text-zinc-300 hover:text-white border border-zinc-800 hover:border-zinc-700 transition-[background-color,border-color,color] font-mono text-[11px] focus-visible-ring"
          >
            <span className="font-semibold text-white">{repo.name}</span>
            <span className="text-[10px] text-zinc-500">({repo.tag})</span>
          </button>
        ))}
      </div>
    </div>
  );
}
