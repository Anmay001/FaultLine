# FaultLine — Cloud Deployment Guide

This guide outlines how to deploy **FaultLine** so judges and users can interact with the live platform.

---

## 🏗️ Architecture Overview

FaultLine consists of:
1. **Frontend**: Next.js 14 (React, Tailwind CSS, Recharts) $\rightarrow$ Deployed to **Vercel**.
2. **Backend**: FastAPI (Python 3.11+, Git CLI, SQLite, Gemini LLM) $\rightarrow$ Deployed to **Render**, **Railway**, or **Koyeb**.

---

## 🚀 Step 1: Push Code to GitHub

Initialize your repository and push to GitHub:

```bash
git init
git add .
git commit -m "feat: initial FaultLine commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

*(The `.gitignore` is already configured to keep your private `.env` and `.venv` safe!)*

---

## 🐍 Step 2: Deploy Backend to Render (Free & Easy)

1. Go to [render.com](https://render.com) and sign in.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository.
4. Configure the service settings:
   - **Name**: `faultline-api`
   - **Root Directory**: `backend` (or leave blank if using Docker)
   - **Runtime**: `Python 3` (or choose `Docker` to use the provided `backend/Dockerfile`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: `<Your-Gemini-API-Key>`
   - `SANDBOX_BASE_DIR`: `/tmp/faultline`
   - `PYTHONUNBUFFERED`: `1`
6. Click **Deploy Web Service**.
7. Once deployed, copy your backend URL (e.g. `https://faultline-api.onrender.com`).

*(Your health check endpoint will be `https://faultline-api.onrender.com/api/health`)*

---

## ⚡ Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in.
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository.
4. In the project configuration:
   - **Root Directory**: Click *Edit* and select **`frontend`**.
   - **Framework Preset**: `Next.js` (automatically detected).
5. Expand **Environment Variables** and add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://faultline-api.onrender.com/api` *(replace with your Render backend URL)*
6. Click **Deploy**.

---

## 🧪 Alternative: Quick Live Demo via Cloudflare Tunnel / ngrok (Zero Cloud Setup)

If you prefer to stream your running local machine backend to judges instantly:

```bash
# 1. Start your local backend (port 8000)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --port 8000

# 2. Expose it via Cloudflare Quick Tunnel (Free, no account needed)
npx -y cloudflared tunnel --url http://localhost:8000
```

Copy the generated public URL (e.g., `https://random-subdomain.trycloudflare.com/api`) and set it as `NEXT_PUBLIC_API_URL` on your Vercel deployment!
