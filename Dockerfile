# Dockerfile — packages your app into a container
#
# CONCEPT: A Docker image is like a snapshot of a computer that has exactly
# what your app needs — Python, your code, and all dependencies.
# It runs identically on your laptop, on Cloud Run, anywhere.
#
# CONCEPT: Each line is a "layer". Docker caches layers — if requirements.txt
# hasn't changed, it skips reinstalling packages. That's why we copy
# requirements.txt BEFORE copying the rest of the code.

# Base image — official Python 3.11, slim variant (smaller image size)
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# CONCEPT: Install system dependencies first (layer cached separately).
# PyMuPDF (fitz) needs these native libs.
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first — so this layer is cached unless deps change
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# CONCEPT: SentenceTransformer downloads the model on first run by default.
# We pre-download it here so it's baked into the image — faster cold starts
# and no network call at runtime.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the app code
COPY . .

# CONCEPT: We do NOT copy .env into the image — that would bake secrets into
# the image. Instead, secrets are injected as environment variables by
# Cloud Run at runtime. The container stays secret-free.

# Create the ChromaDB persistence directory
RUN mkdir -p /app/chroma_db

# CONCEPT: PORT 8080 is what Google Cloud Run expects by default.
# We expose it here so Cloud Run knows which port to route traffic to.
EXPOSE 8080

# CONCEPT: This is what runs when the container starts.
# uvicorn = the ASGI server that runs FastAPI.
# --host 0.0.0.0 = accept connections from outside the container (required).
# --port 8080 = match Cloud Run's expected port.
# --workers 1 = one process (ChromaDB singleton is not multi-process safe).
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]