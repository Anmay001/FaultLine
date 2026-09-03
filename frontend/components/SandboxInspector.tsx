"use client";

import React, { useEffect, useState } from "react";
import { X, FileCode, Search, Terminal, Copy, Check } from "lucide-react";
import { getSandboxFileContent, listSandboxFiles } from "@/lib/api";

interface SandboxInspectorProps {
  analysisId: string;
  initialFile?: string | null;
  onClose: () => void;
}

export default function SandboxInspector({
  analysisId,
  initialFile,
  onClose,
}: SandboxInspectorProps) {
  const [files, setFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(initialFile || null);
  const [fileContent, setFileContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [filterQuery, setFilterQuery] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    listSandboxFiles(analysisId)
      .then((data) => {
        setFiles(data.files || []);
        if (!selectedFile && data.files.length > 0) {
          setSelectedFile(data.files[0]);
        }
      })
      .catch(() => {});
  }, [analysisId]);

  useEffect(() => {
    if (selectedFile) {
      setIsLoading(true);
      getSandboxFileContent(analysisId, selectedFile)
        .then((res) => setFileContent(res.content))
        .catch((err) => setFileContent(`Error loading file: ${err.message}`))
        .finally(() => setIsLoading(false));
    }
  }, [analysisId, selectedFile]);

  const handleCopy = () => {
    navigator.clipboard.writeText(fileContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClose = (e: React.KeyboardEvent | React.MouseEvent) => {
    if (e.type === "click") {
      e.preventDefault();
      onClose();
    } else if (e.type === "keydown") {
      const ke = e as React.KeyboardEvent;
      if (ke.key === "Enter" || ke.key === " ") {
        ke.preventDefault();
        onClose();
      }
    }
  };

  const filteredFiles = files.filter((f) =>
    f.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200 modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="sandbox-title"
      tabIndex={-1}
    >
      <div className="relative w-full max-w-5xl h-[80vh] flex flex-col rounded-3xl glass-panel border border-zinc-800 shadow-2xl overflow-hidden bg-black drawer">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-950">
          <div className="flex items-center gap-2.5">
            <FileCode className="w-5 h-5 text-white" aria-hidden="true" />
            <h2 id="sandbox-title" className="font-bold text-sm text-white">
              Repository File Explorer
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-800 font-mono">
              Files & Source Code
            </span>
          </div>

          <button
            onClick={handleClose}
            onKeyDown={handleClose}
            className="p-1.5 rounded-xl hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors focus-visible-ring"
            aria-label="Close file explorer"
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* File Tree Sidebar */}
          <aside className="w-72 border-r border-zinc-800 bg-zinc-950 flex flex-col" aria-label="File tree">
            <div className="p-3 border-b border-zinc-800">
              <label htmlFor="file-filter" className="sr-only">Filter repository files</label>
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-zinc-500 pointer-events-none" aria-hidden="true" />
                <input
                  type="search"
                  id="file-filter"
                  placeholder="Filter repository files…"
                  value={filterQuery}
                  onChange={(e) => setFilterQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 font-mono focus-visible-ring"
                  autoComplete="off"
                  spellCheck={false}
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1 font-mono text-xs" role="tree" aria-label="Repository files">
              {filteredFiles.map((file) => (
                <button
                  key={file}
                  onClick={() => setSelectedFile(file)}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left truncate transition-colors ${
                    selectedFile === file
                      ? "bg-white text-black font-bold shadow-sm"
                      : "text-zinc-400 hover:text-white hover:bg-zinc-900"
                  } focus-visible-ring`}
                  role="treeitem"
                  aria-selected={selectedFile === file}
                >
                  <FileCode className="w-3.5 h-3.5 flex-shrink-0 opacity-70" aria-hidden="true" />
                  <span className="truncate">{file}</span>
                </button>
              ))}
              {filteredFiles.length === 0 && (
                <p className="px-2.5 py-1.5 text-zinc-500 text-center">No files match filter</p>
              )}
            </div>
          </aside>

          {/* Code Viewer */}
          <div className="flex-1 flex flex-col bg-black">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-zinc-800 bg-zinc-950 text-xs">
              <label htmlFor="code-viewer" className="sr-only">File content</label>
              <span className="font-mono text-zinc-300 font-semibold">{selectedFile || "No file selected"}</span>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 transition-colors font-mono text-[11px] focus-visible-ring"
                aria-label={copied ? "Copied to clipboard" : "Copy file content to clipboard"}
              >
                {copied ? <Check className="w-3 h-3 text-white" aria-hidden="true" /> : <Copy className="w-3 h-3 text-zinc-400" aria-hidden="true" />}
                <span>{copied ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 font-mono text-xs text-zinc-200 bg-black leading-relaxed" id="code-viewer" role="region" aria-label="File content" tabIndex={0}>
              {isLoading ? (
                <div className="flex items-center justify-center h-full text-zinc-500 font-mono">
                  <span>Loading sandbox file&hellip;</span>
                </div>
              ) : (
                <pre className="whitespace-pre">{fileContent || "No content"}</pre>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
