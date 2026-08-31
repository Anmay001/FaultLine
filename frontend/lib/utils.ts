import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score?: number | null): string {
  if (score === null || score === undefined) return "N/A";
  return score.toFixed(1);
}

export function getScoreColor(score?: number | null): {
  text: string;
  bg: string;
  border: string;
  ring: string;
  stroke: string;
  label: string;
} {
  if (score === null || score === undefined) {
    return {
      text: "text-zinc-500",
      bg: "bg-zinc-900/50",
      border: "border-zinc-800",
      ring: "ring-zinc-800",
      stroke: "#52525b",
      label: "PENDING",
    };
  }
  if (score >= 80) {
    return {
      text: "text-white",
      bg: "bg-zinc-900",
      border: "border-zinc-400",
      ring: "ring-zinc-400",
      stroke: "#ffffff",
      label: "EXCELLENT",
    };
  }
  if (score >= 65) {
    return {
      text: "text-zinc-200",
      bg: "bg-zinc-900/80",
      border: "border-zinc-600",
      ring: "ring-zinc-600",
      stroke: "#d4d4d8",
      label: "MODERATE RISK",
    };
  }
  if (score >= 45) {
    return {
      text: "text-zinc-300",
      bg: "bg-zinc-900/60",
      border: "border-zinc-700",
      ring: "ring-zinc-700",
      stroke: "#a1a1aa",
      label: "ELEVATED RISK",
    };
  }
  return {
    text: "text-zinc-400",
    bg: "bg-zinc-950",
    border: "border-zinc-800",
    ring: "ring-zinc-800",
    stroke: "#71717a",
    label: "CRITICAL RISK",
  };
}

export function getSeverityBadge(severity: string) {
  switch (severity.toUpperCase()) {
    case "CRITICAL":
      return {
        bg: "bg-white text-black border-white font-black shadow-sm",
        label: "CRITICAL",
      };
    case "HIGH":
      return {
        bg: "bg-zinc-800 text-zinc-100 border-zinc-600 font-bold",
        label: "HIGH",
      };
    case "MEDIUM":
      return {
        bg: "bg-zinc-900 text-zinc-300 border-zinc-700 font-medium",
        label: "MEDIUM",
      };
    case "LOW":
    default:
      return {
        bg: "bg-black text-zinc-400 border-zinc-800 font-medium",
        label: "LOW",
      };
  }
}
