# FaultLine — Reproduction & Judge Evaluation Guide

This guide provides step-by-step, copy-pasteable instructions for hackathon judges to verify and evaluate **FaultLine** locally from a clean environment, or inspect the live cloud deployment.

---

## ⚡ Quick Evaluation Summary

| Attribute | Specification |
| :--- | :--- |
| **Expected Benchmark Runtime** | **$\sim 15 - 25$ Seconds** |
| **API Cost** | **$0.00 (100% Free)** via intelligent built-in `MockLLMProvider` (or use Gemini API key) |
| **Live Cloud Demo** | **[https://faultline-woad.vercel.app](https://faultline-woad.vercel.app)** |
| **Live Backend API** | **[https://faultline-b031.onrender.com/api/health](https://faultline-b031.onrender.com/api/health)** |

---

## 📦 Prerequisites

Ensure your host machine has:
1. **Python 3.11+** (Tested on Python 3.11, 3.12, 3.13, 3.14)
2. **Node.js 18+** & **npm** (for Frontend)
3. **Git CLI** (installed and available in system `PATH`)
4. *(Optional)* **Docker & Docker Compose** (for single-command containerized execution)

---

## 🧪 Option 1: Run the Quantitative Benchmark in 20 Seconds (Fastest)

Run our automated comparative benchmark script to evaluate **FaultLine** against a single-prompt LLM baseline on 3 ground-truth test repositories:

### On Linux / macOS:
```bash
# 1. Clone repository
git clone https://github.com/Anmay001/FaultLine.git
cd FaultLine

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Generate synthetic benchmark repos & execute evaluation
python benchmark/setup_repos.py
python benchmark/run_evaluation.py
```

### On Windows (PowerShell):
```powershell
# 1. Clone repository
git clone https://github.com/Anmay001/FaultLine.git
cd FaultLine

# 2. Set up virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Generate synthetic benchmark repos & execute evaluation
python benchmark/setup_repos.py
python benchmark/run_evaluation.py
```

### Run Unit & Integration Tests:
```bash
pytest -v
```
*(Expected: 29 passed in $\sim 10$ seconds)*

---

## 🖥️ Option 2: Run Full-Stack Web Application Locally

To explore the Next.js interactive UI and live sandbox inspection dashboard on your machine:

### 1. Start the FastAPI Backend (Port 8000)
```bash
# In Terminal 1 (from repository root):
# (Ensure .venv is activated)
uvicorn app.main:app --app-dir backend --port 8000 --reload
```
- Verify health check: `http://localhost:8000/api/health`
- Swagger interactive API docs: `http://localhost:8000/docs`

### 2. Start the Next.js Frontend (Port 3000)
```bash
# In Terminal 2 (from repository root):
cd frontend
npm install
npm run dev
```
- Open your browser at **`http://localhost:3000`**
- Click any sample target (e.g. **FastAPI**, **Flask**, **Express**) or paste any public GitHub repository URL!

---

## 🐳 Option 3: Run with Docker Compose

If you have Docker installed, you can launch the complete full-stack platform with a single command:

```bash
docker compose up --build
```
- **Frontend Dashboard**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`

---

## 🔑 Environment Variables (Optional)

FaultLine operates **100% offline and free** by default using deterministic AST tools and high-fidelity mock LLM reasoning.

If you wish to test with live Google Gemini AI:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your Gemini API key:
   ```env
   GEMINI_API_KEY="your-gemini-api-key"
   DEFAULT_LLM_MODEL="gemini-2.0-flash"
   ```
