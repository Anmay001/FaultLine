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

## 🌐 Cloud Deployment (Vercel & Render)

For step-by-step instructions on deploying the frontend to **Vercel** and the backend to **Render / Railway**, see the [Cloud Deployment Guide](docs/DEPLOYMENT.md).
