# FaultLine — Agentic Software-Project Failure & Risk Detection

> **Autonomous multi-agent intelligence platform that detects software project failures, structural risks, and velocity degradation using deterministic AST, static analysis, test health, and sandbox ground-truth verification.**

---

## 🌟 Executive Summary & Evaluation Benchmark

Unlike traditional LLMs that speculate on code quality through high-level directory prompts, **FaultLine** deploys 7 specialized agents into an ephemeral sandbox, correlates multi-modal signals, and validates every claim against the ground-truth filesystem before computing a mathematically weighted score (0–100).

### Quantitative Benchmark Results (Baseline vs. FaultLine)

| Metric | Single-Prompt Baseline | FaultLine Multi-Agent Platform | Improvement / Advantage |
| :--- | :--- | :--- | :--- |
| **Evidence Accuracy** | **61.1%** | **100.0%** | **+38.9% Ground-Truth Proofs** |
| **Finding Precision** | **61.1%** | **91.1%** | **+30.0% Reduction in Hallucinations** |
| **Ground-Truth Verification Rate** | **0.0%** | **91.1%** | **Sandbox Automated Proofs** |
| **Compounded Hotspots Discovered** | **0** | **1** | **Multi-Signal Cross-Agent Correlation** |
| **Scoring Determinism** | Speculative / Hallucinated | Mathematical Weighted (0-100) | Strictly Reproducible |

### Detailed Repository Breakdown

| Repository Target | System | Health Score | Total Findings | Verified Proofs | Precision | Evidence Accuracy | Verification Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `repo_healthy` | **Baseline** | 85.0/100 | 1 | 0 | 100.0% | 100.0% | 0.0% |
| `repo_healthy` | **FaultLine** | **98.6/100** | 1 | 1 | **100.0%** | **100.0%** | **100.0%** |
| `repo_dependency_risk` | **Baseline** | 72.0/100 | 2 | 0 | 50.0% | 50.0% | 0.0% |
| `repo_dependency_risk` | **FaultLine** | **86.8/100** | 8 | 7 | **87.5%** | **100.0%** | **87.5%** |
| `repo_high_churn_no_tests` | **Baseline** | 68.0/100 | 3 | 0 | 33.3% | 33.3% | 0.0% |
| `repo_high_churn_no_tests` | **FaultLine** | **59.3/100** | 14 | 12 | **85.7%** | **100.0%** | **85.7%** |

---

## 🏛️ System Architecture

```
                                  [ User Input: Git Repo URL ]
                                               │
                                               ▼
                               ┌──────────────────────────────────┐
                               │  Ephemeral Sandbox Cloner & VFS  │
                               └──────────────────────────────────┘
                                               │
               ┌───────────────────────────────┼──────────────────────────────┐
               ▼                               ▼                              ▼
    ┌────────────────────┐          ┌────────────────────┐         ┌────────────────────┐
    │  Repo Scout Agent  │          │  Code Risk Agent   │         │ Test Health Agent  │
    └────────────────────┘          └────────────────────┘         └────────────────────┘
               ▼                               ▼                              ▼
    ┌────────────────────┐          ┌────────────────────┐         ┌────────────────────┐
    │ Dependency Agent   │          │ Git History Agent  │         │ Architecture Agent │
    └────────────────────┘          └────────────────────┘         └────────────────────┘
               └───────────────────────────────┬──────────────────────────────┘
                                               │
                                               ▼
                               ┌──────────────────────────────────┐
                               │     Risk Correlation Agent       │
                               │ (Surfaces Compounded Hotspots)   │
                               └──────────────────────────────────┘
                                               │
                                               ▼
                               ┌──────────────────────────────────┐
                               │    Ground-Truth Verification     │
                               │ (AST & File Bounds Proof Filter) │
                               └──────────────────────────────────┘
                                               │
                                               ▼
                               ┌──────────────────────────────────┐
                               │     Deterministic Synthesizer    │
                               │  (Weighted Formula Score 0-100)  │
                               └──────────────────────────────────┘
                                               │
                                               ▼
                               ┌──────────────────────────────────┐
                               │   Next.js 14 Monochrome UI       │
                               └──────────────────────────────────┘
```

### Deterministic Category Scoring Formula
$$\text{Score}_{\text{final}} = 0.25 \cdot S_{\text{code}} + 0.20 \cdot S_{\text{test}} + 0.20 \cdot S_{\text{git}} + 0.15 \cdot S_{\text{dep}} + 0.10 \cdot S_{\text{arch}} + 0.10 \cdot S_{\text{doc}}$$

Where:
- $\text{Penalty} = \text{Severity Weight} \times \text{Verification Multiplier}$
- $\text{Verification Multipliers}$: `VERIFIED` = 1.0, `INSUFFICIENT_EVIDENCE` = 0.6, `NOT_VERIFIED` = 0.0 (unverified claims never degrade scores).

---

## 🚀 Quickstart Guide

### 1. Backend (FastAPI + SQLite + Agents)
```bash
# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt

# Run automated test suite (29 tests)
pytest backend/tests -v

# Start FastAPI backend
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

### 2. Frontend Dashboard (Next.js 14 + Tailwind + Recharts)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 3. Run Benchmark Suite
```bash
python benchmark/setup_repos.py
python benchmark/run_evaluation.py
```

---

## 🗺️ Product Roadmap & Future Vision

FaultLine is built on an **Open-Core** developer-first commercialization strategy:

```
[ Phase 1: Open-Core Foundation ] ──► [ Phase 2: Cloud & Teams ($29/mo) ] ──► [ Phase 3: CI/CD Gatekeeping ] ──► [ Phase 4: Auto-Remediation ("Fix") ]
```

- **Phase 1: Open-Core Engine (Current)**: 100% open-source local CLI, 7 domain agents, sandbox verification, zero cloud telemetry.
- **Phase 2: FaultLine Cloud & Team Workspaces (Q4 2026)**: GitHub/Google OAuth, PostgreSQL + Redis queues, Pro ($29/dev/mo) & Enterprise tiers with private repos and SOC2 audit logs.
- **Phase 3: Active CI/CD PR Bot & Gatekeeping (Q1 2027)**: GitHub Action blocking risky merges, inline sticky PR failure proofs, and risk drift tracking over time.
- **Phase 4: Autonomous Remediation ("FaultLine Fix") (Q2 2027+)**: AI generates missing regression test suites for untested hotspots, opening ready-to-merge draft PRs, plus VS Code & JetBrains extensions.

For the full commercial strategy, user personas, and financial architecture, see [docs/ROADMAP.md](docs/ROADMAP.md).

---

## 📚 Complete Documentation Index

- 🗺️ **[Commercial Roadmap & SaaS Vision](docs/ROADMAP.md)**: Open-core business model, 4-phase rollout, and tiering structure.
- 🧪 **[Reproduction & Evaluation Guide](docs/REPRODUCTION.md)**: Fast judge verification, local environment setup, and benchmark execution.
- 🧭 **[Multi-Agent Trajectories Trace](docs/TRAJECTORIES.md)**: Complete step-by-step trace from prompt to AST tools, correlation, and sandbox verification.
- 📅 **[Engineering Changelog](docs/CHANGELOG.md)**: 4 core iterations, the removed 10-micro-agent experiment, and our core philosophy.
- 🌐 **[Cloud Deployment Guide](docs/DEPLOYMENT.md)**: Architecture overview for Vercel and Render deployments.

