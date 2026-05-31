# AskMyPDF — Deployment Guide
# From local FastAPI → live Google Cloud Run URL

# ═══════════════════════════════════════════════════════════
# STEP 1 — Run locally first (always test before deploying)
# ═══════════════════════════════════════════════════════════

# 1a. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 1b. Install dependencies
pip install -r requirements.txt

# 1c. Create your .env file
copy .env.example .env
# Then open .env and add your real GEMINI_API_KEY

# 1d. Start the FastAPI server
uvicorn api:app --reload --port 8000

# 1e. Open in browser — interactive API docs (auto-generated, free!)
# http://localhost:8000/docs
#
# Test it:
#   POST /upload  → upload a PDF
#   POST /ask     → ask a question
#   GET  /status  → see what's indexed


# ═══════════════════════════════════════════════════════════
# STEP 2 — Build and test Docker locally
# ═══════════════════════════════════════════════════════════

# 2a. Build the image (first time is slow — downloads model)
docker build -t askmypdf .

# 2b. Run the container locally
# CONCEPT: -e passes your secret as an environment variable at runtime.
# The container never has the key baked in — it receives it when it starts.
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key_here askmypdf

# 2c. Test at http://localhost:8080/docs
# If it works here, it will work on Cloud Run.


# ═══════════════════════════════════════════════════════════
# STEP 3 — Set up Google Cloud (one-time)
# ═══════════════════════════════════════════════════════════

# 3a. Install Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# 3b. Login and create project
gcloud auth login
gcloud projects create askmypdf-project --name="AskMyPDF"
gcloud config set project askmypdf-project

# 3c. Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# 3d. Create Artifact Registry repo (stores your Docker images)
gcloud artifacts repositories create askmypdf-repo \
    --repository-format=docker \
    --location=us-central1


# ═══════════════════════════════════════════════════════════
# STEP 4 — Push image to Google Cloud
# ═══════════════════════════════════════════════════════════

# 4a. Configure Docker to use gcloud for authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# 4b. Tag your image with the registry path
docker tag askmypdf \
    us-central1-docker.pkg.dev/askmypdf-project/askmypdf-repo/askmypdf:latest

# 4c. Push the image
docker push \
    us-central1-docker.pkg.dev/askmypdf-project/askmypdf-repo/askmypdf:latest

# CONCEPT: Your image now lives in Google's private registry.
# Cloud Run will pull it from here when it starts containers.


# ═══════════════════════════════════════════════════════════
# STEP 5 — Deploy to Cloud Run
# ═══════════════════════════════════════════════════════════

gcloud run deploy askmypdf \
    --image us-central1-docker.pkg.dev/askmypdf-project/askmypdf-repo/askmypdf:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --set-env-vars GEMINI_API_KEY=your_actual_key_here

# CONCEPT: --min-instances 0 = scales to zero when no traffic (free tier).
# CONCEPT: --max-instances 3 = auto-scales up to 3 containers under load.
# CONCEPT: --memory 2Gi = SentenceTransformer model needs ~500MB RAM.

# After deploy, you get a URL like:
# https://askmypdf-xxxxxxxx-uc.a.run.app
#
# Visit https://askmypdf-xxxxxxxx-uc.a.run.app/docs
# Your API is live!


# ═══════════════════════════════════════════════════════════
# STEP 6 — Monitoring (takes 5 minutes)
# ═══════════════════════════════════════════════════════════

# View live logs:
gcloud run services logs read askmypdf --region us-central1 --limit 50

# Or in GCP Console:
# https://console.cloud.google.com/run
# Click your service → Logs tab
# CONCEPT: Every request, error, and print() statement appears here.

# Set a billing alert so you never get surprised:
# GCP Console → Billing → Budgets & Alerts → Create Budget
# Set amount: $1. You'll email when spend reaches $0.50 and $1.00.
# CONCEPT: Cloud Run free tier = 2M requests/month. For a portfolio project
# you'll never pay anything. But the alert is good practice.


# ═══════════════════════════════════════════════════════════
# STEP 7 — Push to GitHub (your portfolio)
# ═══════════════════════════════════════════════════════════

git init
git add .
git commit -m "AskMyPDF: RAG chatbot with FastAPI + Cloud Run deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/askmypdf.git
git push -u origin main

# Your recruiter can now:
# 1. See the code on GitHub
# 2. Hit your live API URL at /docs and test it themselves
# That's a real portfolio project.