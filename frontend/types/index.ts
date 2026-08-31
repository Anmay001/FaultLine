export type RiskCategory =
  | "CODE"
  | "TEST"
  | "GIT"
  | "DEPENDENCY"
  | "ARCHITECTURE"
  | "DOCUMENTATION"
  | "COMPOUNDED";

export type RiskSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export type VerificationStatus = "VERIFIED" | "NOT_VERIFIED" | "INSUFFICIENT_EVIDENCE";

export type AnalysisStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

export interface Evidence {
  id: string;
  finding_id: string;
  type: "code" | "git" | "test" | "dependency" | "architecture" | "documentation";
  file: string;
  line_start?: number | null;
  line_end?: number | null;
  description: string;
  snippet?: string | null;
  created_at?: string;
}

export interface Finding {
  id: string;
  analysis_run_id: string;
  finding: string;
  category: RiskCategory;
  severity: RiskSeverity;
  confidence: number;
  verification_status: VerificationStatus;
  verification_notes?: string | null;
  created_at?: string;
  evidence: Evidence[];
}

export interface AnalysisRun {
  id: string;
  repository_id: string;
  status: AnalysisStatus;
  commit_hash?: string | null;
  branch?: string | null;
  overall_score?: number | null;
  code_risk_score?: number | null;
  test_risk_score?: number | null;
  git_risk_score?: number | null;
  dependency_risk_score?: number | null;
  architecture_risk_score?: number | null;
  documentation_risk_score?: number | null;
  summary?: string | null;
  error_message?: string | null;
  sandbox_path?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  findings: Finding[];
}

export interface Repository {
  id: string;
  url: string;
  name: string;
  owner: string;
  default_branch: string;
  created_at: string;
  updated_at: string;
  analysis_runs: AnalysisRun[];
}

export interface AnalysisTriggerPayload {
  repo_url: string;
  branch?: string;
  shallow_depth?: number;
}
