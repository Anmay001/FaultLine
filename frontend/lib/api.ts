import { AnalysisRun, AnalysisTriggerPayload, Repository } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api-proxy";

export async function checkBackendHealth(): Promise<{ status: string; version: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    if (!res.ok) throw new Error("Health check failed");
    return await res.json();
  } catch (error) {
    return { status: "disconnected", version: "unknown" };
  }
}

export async function triggerAnalysis(payload: AnalysisTriggerPayload): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE_URL}/analyses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let errorMsg = `Server returned HTTP ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData?.detail) errorMsg = errorData.detail;
    } catch {}
    throw new Error(errorMsg);
  }

  return await res.json();
}

export async function getAnalysis(analysisId: string): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE_URL}/analyses/${analysisId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch analysis details");
  }

  return await res.json();
}

export async function listAnalyses(limit: number = 20): Promise<AnalysisRun[]> {
  const res = await fetch(`${API_BASE_URL}/analyses?limit=${limit}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch analysis list");
  }

  return await res.json();
}

export async function listRepositories(): Promise<Repository[]> {
  const res = await fetch(`${API_BASE_URL}/repositories`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch repositories");
  }

  return await res.json();
}

export async function listSandboxFiles(analysisId: string): Promise<{ files: string[]; count: number }> {
  const res = await fetch(`${API_BASE_URL}/sandboxes/${analysisId}/files`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch sandbox files");
  }

  return await res.json();
}

export async function getSandboxFileContent(analysisId: string, filePath: string): Promise<{ content: string }> {
  const res = await fetch(
    `${API_BASE_URL}/sandboxes/${analysisId}/file-content?file_path=${encodeURIComponent(filePath)}`,
    { cache: "no-store" }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch file content");
  }

  return await res.json();
}
