# 🚀 Deployment Guide

## Overview

This project can be deployed in multiple ways depending on your use case:

1. **Terminal UI (Current)** - Rich TUI for local development
2. **Web UI (Streamlit)** - For sharing with stakeholders
3. **Docker Container** - For reproducible deployments
4. **Cloud Platform** - For 24/7 operation

---

## Option 1: Terminal UI (Local)

**Best for:** Development, debugging, hackathon demos

```bash
uv run python main.py
```

**Pros:**
- ✅ Fast, direct execution
- ✅ Real-time updates
- ✅ Full control

**Cons:**
- ❌ Requires terminal access
- ❌ Not shareable via URL

---

## Option 2: Streamlit Web UI

**Best for:** Sharing with non-technical users, presentations

### Setup

1. Create `app_web.py`:
```bash
uv add streamlit plotly
```

2. Run locally:
```bash
streamlit run app_web.py
```

3. Deploy to Streamlit Community Cloud:
   - Push to GitHub
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your repo
   - **Add secrets** (API keys) in the Streamlit dashboard

**Pros:**
- ✅ Zero infrastructure setup
-  ✅ Free tier available
- ✅ Shareable URL

**Cons:**
- ❌ Limited compute (free tier)
- ❌ Public by default

---

## Option 3: Docker Deployment

**Best for:** Reproducible environments, cloud platforms

### Dockerfile (Already included)

```bash
# Build
docker build -t agent-market .

# Run
docker run --env-file .env agent-market
```

### Deploy to Cloud Run (Google Cloud)

```bash
gcloud run deploy agent-market \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

**Pros:**
- ✅ Isolation
- ✅ Scales automatically
- ✅ Works on any cloud (GCP, AWS, Azure)

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Cloud costs

---

## Option 4: Render / Railway / Fly.io

**Best for:** Quick, managed deployments

### Render.com (Recommended)

1. Connect GitHub repo
2. Set build command: `uv sync`
3. Set start command: `uv run python main.py`
4. Add environment variables (API keys)

**Free tier:** 750 hours/month

---

## CI/CD Pipeline

The `.github/workflows/ci.yml` automatically:
- ✅ Runs tests on every push
- ✅ Tests across Python 3.10, 3.11, 3.12
- ✅ Generates coverage reports

### Future Enhancements

Add a deployment stage:
```yaml
deploy:
  needs: test
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to Streamlit
      run: |
        # Auto-deploy script here
```

---

## Recommended Path for Hackathon

1. **Demo:** Use Terminal UI (main.py)
2. **Web Version:** Add Streamlit UI for judges
3. **Production:** Docker + Cloud Run

Let me know which option you'd like me to implement!
