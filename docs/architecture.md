# FaultLine — Master Architecture & System Design Plan

## 1. Executive Summary & Core Philosophy

**FaultLine** is an autonomous, agentic software-project failure and risk detection platform designed to discover, correlate, and verify architectural, code-quality, operational, and development velocity risks.

### Core Tenet
> **LLMs generate hypotheses. Tools provide deterministic evidence. Agents correlate the findings. The Verification Agent proves or disproves claims.**

Traditional LLM code reviews hallucinate non-existent issues and lack ground-truth verification. FaultLine guarantees that **every claim is backed by verifiable, reproducible evidence** extracted via AST parsers, Git logs, static analyzers, test runners, and dependency auditors.

```
                  ┌────────────────────────────────────────┐
                  │          GitHub Repository URL         │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    Docker Sandbox Cloning & Setup      │
                  │   (/tmp/faultline/<analysis_id>/)      │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         Repository Scout Agent         │
                  │  (Languages, Frameworks, Architecture) │
                  └───────────────────┬────────────────────┘
                                      │
        ┌─────────────────────────────┼────────────────────────────┐
        ▼                             ▼                            ▼
┌───────────────┐             ┌───────────────┐            ┌───────────────┐
│   Code Risk   │             │  Test Health  │            │  Dependency   │
│     Agent     │             │     Agent     │            │  Risk Agent   │
└───────┬───────┘             └───────┬───────┘            └───────┬───────┘
        │                             │                            │
        ├─────────────────────────────┼────────────────────────────┤
        │                             │                            │
        ▼                             ▼                            ▼
┌───────────────┐             ┌───────────────┐            ┌───────────────┐
│  Git History  │             │ Documentation │            │ Architecture  │
│     Agent     │             │  Consistency  │            │     Agent     │
└───────┬───────┘             └───────┬───────┘            └───────┬───────┘
        │                             │                            │
        └─────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         Risk Correlation Agent         │
                  │ (Multi-signal Compounded Hotspots)     │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       Verification Agent (Sandbox)     │
                  │ (Reproduction & AST / File Proofs)     │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         Risk Synthesizer Agent         │
                  │ (Deterministic Scoring & Report Gen)   │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      FastAPI Backend & SQLite DB       │
                  │     Next.js / shadcn Interactive UI    │
                  └────────────────────────────────────────┘
```

---

## 2. Technology Stack & Component Specifications

| Layer | Technologies & Libraries | Purpose / Notes |
| :--- | :--- | :--- |
| **Frontend** | Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts, React Flow | High-impact interactive dashboard, dependency graph visualizer, risk matrix, expandable evidence inspection |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite (WAL mode) | Asynchronous API endpoints, orchestration pipeline, structured schemas, persistence |
| **AI Orchestration** | Gemini API (`google-genai` / `LLMProvider` abstraction), `asyncio.gather` parallel execution | Abstracted LLM provider interface for high throughput, strict JSON schema output |
| **Analysis Tooling** | `GitPython`, `tree-sitter`, `ruff`, `pytest`, `coverage`, `eslint`, `tsc`, GitHub REST API | Deterministic code analysis, AST parsing, Git churn/ownership analysis, test execution |
| **Sandbox & Isolation** | Docker, Docker Compose, Secure Linux Sandbox container | Zero-trust repo execution, isolated execution environment, read-only analysis |

---

## 3. Specialized Agents & Responsibilities

### 1. Repository Scout Agent
* **Objective:** Map project topography, detect languages, framework versions, package managers (`npm`, `poetry`, `pip`, `cargo`, `gradle`, etc.), entry points, and test framework configurations.
* **Deterministic Input:** Directory tree walk, manifest file parser (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
* **Output:** `ScoutReport` (Structured repository blueprint).

### 2. Code Risk Agent
* **Objective:** Identify static hotspots, cyclomatic & cognitive complexity, code duplication, antipatterns, security concerns, and dense `TODO`/`FIXME`/`HACK` clusters.
* **Deterministic Input:** Tree-sitter AST queries, Ruff JSON reports, ESLint outputs.
* **Output:** `List[CodeRiskFinding]`.

### 3. Test Health Agent
* **Objective:** Quantify test suite robustness, line/branch coverage, failing/flaky tests, missing test suites on critical business paths, and mock ratio.
* **Deterministic Input:** Pytest/Jest execution outputs, coverage XML/JSON reports.
* **Output:** `List[TestHealthFinding]`.

### 4. Dependency Risk Agent
* **Objective:** Identify outdated packages, known CVE vulnerabilities, major-version drift, deprecated packages, and license/conflict risks.
* **Deterministic Input:** Dependency lockfile parsers (`package-lock.json`, `poetry.lock`), vulnerability databases / safety checks.
* **Output:** `List[DependencyRiskFinding]`.

### 5. Git History Agent
* **Objective:** Detect project velocity bottlenecks: churn hotspots (frequently modified files), bug-fix commit clustering, reverted commits, bus factor (developer ownership concentration), and high defect-density areas.
* **Deterministic Input:** Git log analysis via GitPython (commit history, churn matrices, diff stats, author contributions).
* **Output:** `List[GitHistoryFinding]`.

### 6. Documentation Consistency Agent
* **Objective:** Detect documentation drift between `README.md`, API documentation, docstrings, and actual exported methods/endpoints/arguments.
* **Deterministic Input:** Markdown parsers + AST exported symbol matchers.
* **Output:** `List[DocConsistencyFinding]`.

### 7. Architecture Agent
* **Objective:** Construct import/dependency graph across modules, detect circular dependencies, layer violations, and central architectural bottlenecks.
* **Deterministic Input:** Module import graphs, Tree-sitter import extractions.
* **Output:** `ArchitectureGraph` + `List[ArchitectureRiskFinding]`.

### 8. Risk Correlation Agent
* **Objective:** Merge and compound multi-modal risk signals (e.g., File `checkout.py` has **High Complexity** [Code Risk] + **0% Test Coverage** [Test Risk] + **Modified in 80% of recent commits** [Git Risk] = **Compounded Critical Hotspot**).
* **Deterministic Input:** Combined findings from Agents 1–7.
* **Output:** `List[CorrelatedRiskFinding]`.

### 9. Verification Agent (The Guardrail)
* **Objective:** Verify high-severity and critical findings against the isolated repository sandbox. Validates file existence, exact line numbers, AST patterns, and triggers targeted test reproduction.
* **Output:** Verification status: `VERIFIED`, `NOT_VERIFIED`, or `INSUFFICIENT_EVIDENCE` with verification trace logs.

### 10. Risk Synthesizer Agent
* **Objective:** Aggregate verified signals, calculate deterministic repository health scores, generate executive summaries, and produce final JSON payloads for persistence and presentation.

---

## 4. Deterministic Scoring & Data Contracts

### 4.1 Weighted Category Scoring Model

The overall project health score ($S \in [0, 100]$) is strictly calculated deterministically:

$$S_{total} = 100 - \sum_{i} \left( w_i \cdot R_i \right)$$

Where $R_i \in [0, 100]$ is the penalty score for category $i$, weighted as follows:
* **Code Risk ($w_{code}$):** $25\%$
* **Test Risk ($w_{test}$):** $20\%$
* **Git / Velocity Risk ($w_{git}$):** $20\%$
* **Dependency Risk ($w_{dep}$):** $15\%$
* **Architecture Risk ($w_{arch}$):** $10\%$
* **Documentation Risk ($w_{doc}$):** $10\%$

### 4.2 Standard Evidence Schema

```json
{
  "id": "risk-uuid-v4",
  "finding": "Unprotected Core Payment Handler with Zero Test Coverage and High Churn",
  "category": "CODE | TEST | GIT | DEPENDENCY | ARCHITECTURE | DOCUMENTATION | COMPOUNDED",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "confidence": 0.95,
  "verification_status": "VERIFIED | NOT_VERIFIED | INSUFFICIENT_EVIDENCE",
  "verification_details": {
    "verified_at": "2026-08-30T00:30:00Z",
    "method": "AST_CHECK_AND_TEST_INSPECTION",
    "notes": "Confirmed file src/services/payment.py contains 450 LOC with cyclomatic complexity 24 and 0 matching test fixtures."
  },
  "evidence": [
    {
      "type": "code",
      "file": "src/services/payment.py",
      "line_start": 42,
      "line_end": 98,
      "description": "Payment execution loop lacks exception isolation and contains cyclomatic complexity score of 24."
    },
    {
      "type": "test",
      "file": "tests/test_payment.py",
      "line_start": 1,
      "line_end": 1,
      "description": "File does not exist; coverage report indicates 0.0% coverage for payment.py."
    },
    {
      "type": "git",
      "file": "src/services/payment.py",
      "line_start": 0,
      "line_end": 0,
      "description": "Modified in 34 of the last 40 commits with 12 bugfix commit tags."
    }
  ]
}
```

---

## 5. Security & Isolation Architecture

1. **Docker Sandbox Execution:**
   - Repositories are cloned into ephemeral directories `/tmp/faultline/<analysis-id>/` located strictly within an isolated sandbox container.
2. **Zero Host Secrets Access:**
   - Agents never receive host environment variables, `~/.ssh` keys, or host file-system access.
3. **Read-Only / Non-Destructive Operations:**
   - Sandboxes operate with restricted network access after cloning. No git pushes, PR creation, or mutations to the original repository are permitted.
4. **Execution Limits:**
   - Dynamic tool execution (e.g., running tests or linters) operates under strict timeout (default 30s) and memory caps (1GB) to prevent resource exhaustion or arbitrary code abuse.

---

## 6. Phased Implementation Roadmap

* **Phase 1: Foundation (Backend & Infrastructure)**
  - Project directory structure setup.
  - Docker sandbox and isolation container configuration.
  - FastAPI application bootstrap with CORS, config management, and SQLite schemas (Repositories, Analysis Runs, Findings, Evidence).
  - Sandboxed Git cloner and repository manager.

* **Phase 2: Tooling & Baselines**
  - Tool wrappers: Tree-sitter AST parser, Ruff runner, Git log parser, Coverage analyzer.
  - Baseline Evaluator (Single-shot prompt LLM baseline for benchmark comparisons).

* **Phase 3: Specialized Agents (1 to 7)**
  - Repository Scout Agent.
  - Code Risk, Test Health, Dependency Risk, Git History, Documentation, and Architecture Agents.
  - Pydantic models and structured JSON response validation for all agents.

* **Phase 4: Correlation, Verification & Synthesis**
  - Risk Correlation Agent (Cross-signal compounding logic).
  - Verification Agent (Sandbox proof & reproduction verification).
  - Risk Synthesizer Agent & deterministic scoring engine.

* **Phase 5: Frontend Dashboard**
  - Next.js (App Router) project setup with Tailwind CSS and shadcn/ui.
  - Repository submission flow, real-time analysis status tracker.
  - Comprehensive health score overview, interactive category breakdowns, dependency graph (React Flow), and evidence inspection modals.

* **Phase 6: Evaluation Benchmark**
  - Comparative evaluation script (Baseline LLM vs. FaultLine Multi-Agent Pipeline) across 10 sample repositories.
  - Precision, Recall, Hallucination Rate, and Evidence Accuracy benchmark report generation.

---

## 7. Execution Readiness

All architectural specifications, agent boundaries, data contracts, and security policies are fully established and aligned with the Master System Specification.
