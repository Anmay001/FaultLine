"use client";

import React, { useState } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import { Layers, BarChart3, PieChart } from "lucide-react";

interface CategoryBreakdownProps {
  codeScore?: number | null;
  testScore?: number | null;
  gitScore?: number | null;
  depScore?: number | null;
  archScore?: number | null;
  docScore?: number | null;
}

export default function RadarBreakdown({
  codeScore = 100,
  testScore = 100,
  gitScore = 100,
  depScore = 100,
  archScore = 100,
  docScore = 100,
}: CategoryBreakdownProps) {
  const [chartType, setChartType] = useState<"radar" | "bar">("radar");

  const data = [
    { subject: "Code Quality", score: codeScore ?? 100, weight: "25%", color: "#ffffff" },
    { subject: "Test Suite", score: testScore ?? 100, weight: "20%", color: "#e4e4e7" },
    { subject: "Git Velocity", score: gitScore ?? 100, weight: "20%", color: "#d4d4d8" },
    { subject: "Dependencies", score: depScore ?? 100, weight: "15%", color: "#a1a1aa" },
    { subject: "Architecture", score: archScore ?? 100, weight: "10%", color: "#71717a" },
    { subject: "Documentation", score: docScore ?? 100, weight: "10%", color: "#52525b" },
  ];

  return (
    <div className="flex flex-col p-6 rounded-2xl glass-card border border-zinc-800 shadow-2xl h-full">
      {/* Header with Switcher */}
      <div className="flex items-center justify-between pb-4 border-b border-zinc-800/80 mb-2">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-zinc-900 text-white border border-zinc-700">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-zinc-100">Category Risk Profile</h3>
            <p className="text-[11px] text-zinc-500 font-mono">Deterministic Multi-Agent Score Distribution</p>
          </div>
        </div>

        {/* Toggle View */}
        <div className="flex items-center p-1 rounded-xl bg-zinc-950 border border-zinc-800 text-xs font-mono">
          <button
            onClick={() => setChartType("radar")}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg transition-colors ${
              chartType === "radar"
                ? "bg-white text-black font-bold"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            <PieChart className="w-3.5 h-3.5" />
            <span>Radar</span>
          </button>
          <button
            onClick={() => setChartType("bar")}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg transition-colors ${
              chartType === "bar"
                ? "bg-white text-black font-bold"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Bar</span>
          </button>
        </div>
      </div>

      {/* Chart Visualization */}
      <div className="w-full h-64 mt-2">
        {chartType === "radar" ? (
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
              <PolarGrid stroke="#27272a" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: "#a1a1aa", fontSize: 11, fontWeight: 500 }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fill: "#52525b", fontSize: 9 }}
              />
              <Radar
                name="Health Score"
                dataKey="score"
                stroke="#ffffff"
                strokeWidth={2}
                fill="#ffffff"
                fillOpacity={0.18}
              />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
              <XAxis type="number" domain={[0, 100]} stroke="#52525b" tick={{ fontSize: 10 }} />
              <YAxis
                type="category"
                dataKey="subject"
                stroke="#a1a1aa"
                tick={{ fontSize: 11, fontWeight: 500 }}
                width={90}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#09090b",
                  borderColor: "#27272a",
                  borderRadius: "0.75rem",
                  fontSize: "12px",
                  color: "#ffffff",
                }}
                formatter={(value: any) => [`${value}/100`, "Health Score"]}
              />
              <Bar dataKey="score" radius={[0, 6, 6, 0]}>
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.score >= 80 ? "#ffffff" : entry.score >= 60 ? "#a1a1aa" : "#52525b"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Category Pills Breakdown */}
      <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-zinc-800/80 text-xs">
        {data.map((item) => (
          <div
            key={item.subject}
            className="flex flex-col p-2 rounded-xl bg-zinc-950 border border-zinc-800/80"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-zinc-400">{item.subject}</span>
              <span className="text-[10px] text-zinc-600 font-mono">{item.weight}</span>
            </div>
            <span
              className={`text-sm font-bold mt-0.5 font-mono ${
                item.score >= 80 ? "text-white" : item.score >= 60 ? "text-zinc-300" : "text-zinc-500"
              }`}
            >
              {item.score.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
