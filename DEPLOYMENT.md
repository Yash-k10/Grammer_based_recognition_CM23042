# Deployment Guide — Grammar-Based Pattern Recognition Web Studio

This project is fully configured for automated, 1-click cloud deployment across multiple platforms.

---

## 🚀 Option 1: Render (Recommended — Free Tier)

Render provides free cloud hosting with automatic GitHub deployment on every commit.

### Steps to Deploy on Render:
1. Go to **[dashboard.render.com](https://dashboard.render.com/)** and sign in with GitHub.
2. Click **New +** -> **Web Service** (or **Blueprint** to use `render.yaml`).
3. Connect your repository: `Yash-k10/Grammer_based_recognition_CM23042`.
4. Configure the service:
   - **Name**: `grammar-pattern-recognition`
   - **Language**: `Python 3`
   - **Region**: Choose closest to you (e.g. Frankfurt, Oregon, Singapore)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: `Free`
5. Click **Deploy Web Service**.
6. Within 2-3 minutes, your web application will be live at `https://<your-service-name>.onrender.com`!

---

## 🚂 Option 2: Railway (Alternative Free/Hobby Cloud)

1. Sign in at **[railway.app](https://railway.app/)** with your GitHub account.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `Grammer_based_recognition_CM23042`.
4. Railway automatically detects `Procfile` and `requirements.txt` and starts building.
5. Under service settings, click **Generate Domain** to get your public HTTPS URL.

---

## ▲ Option 3: Vercel (Serverless)

1. Go to **[vercel.com](https://vercel.com/)** and log in.
2. Click **Add New...** -> **Project**.
3. Import `Grammer_based_recognition_CM23042`.
4. The project includes `vercel.json` and `api/index.py` configured for Vercel's Python runtime.
5. Click **Deploy**.

---

## 🐳 Option 4: Docker Container (Any Cloud or VPS)

A multi-stage `Dockerfile` is included with native Graphviz binaries and Gunicorn pre-installed:

### Build and Run Locally:
```bash
docker build -t grammar-pattern-studio .
docker run -d -p 5000:5000 --name grammar-app grammar-pattern-studio
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 🩺 Health Check Endpoint

All platforms can use the built-in health check endpoint:
- **URL**: `GET /health`
- **Response**: `{"status": "healthy", "service": "grammar-pattern-recognition"}`
