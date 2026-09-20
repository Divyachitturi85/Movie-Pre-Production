# Deployment & Installation Guide

This document provides complete instructions for installing, configuring, and deploying the **AI-Powered Movie Pre-Production Planning & Production Management System** across local development environments, Docker containers, and production servers.

---

## 1. System Requirements & Prerequisites

### 1.1 Hardware Specifications
- **CPU**: Dual-core x86-64 / ARM64 minimum (Quad-core or higher recommended for fast PyTorch & PaddleOCR inference).
- **RAM**: 4 GB minimum (8 GB recommended for Hugging Face BERT NER in-memory execution).
- **Disk Storage**: 3 GB free disk space (to store PyTorch, spaCy language models, and Hugging Face model cache).

### 1.2 Software Prerequisites
- **Python**: 3.10, 3.11, or 3.12 (`python --version`)
- **Node.js**: 18.x or 20.x LTS (`node -v`)
- **Package Managers**: `pip` and `npm`
- **Operating Systems**: Windows 10/11, macOS (Apple Silicon/Intel), Ubuntu 20.04/22.04 LTS

---

## 2. Local Development Setup

### 2.1 Backend Setup (FastAPI)

1. Open PowerShell or Terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the spaCy English linguistic model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Configure environment variables (create `.env` in `backend/`):
   ```env
   PROJECT_NAME="AI-Powered Movie Pre-Production System"
   DATABASE_URL="sqlite:///./movie_preproduction.db"
   CORS_ORIGINS='["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173"]'
   UPLOAD_DIR="./uploads"
   EXPORTS_DIR="./exports"
   HUGGINGFACE_NER_MODEL="dslim/bert-base-NER"
   USE_PADDLEOCR=true
   LOG_LEVEL="INFO"
   ```

6. Launch the FastAPI backend server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - Swagger OpenAPI Docs: `http://127.0.0.1:8000/docs`
   - ReDoc Documentation: `http://127.0.0.1:8000/redoc`
   - API Health Check: `http://127.0.0.1:8000/api/health`

---

### 2.2 Frontend Setup (React + Vite + Tailwind)

1. Open a second terminal window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Configure frontend environment variables (create `.env` in `frontend/`):
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

4. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   The UI will be accessible at `http://localhost:5173`.

---

## 3. Production Build & Static Serving

To build the optimized frontend single-page application for production:

1. Compile the production bundle:
   ```bash
   cd frontend
   npm run build
   ```
   This generates pre-compressed, tree-shaken static assets inside `frontend/dist/`.

2. Test the production bundle locally:
   ```bash
   npm run preview
   ```

3. Serve with Nginx or configure FastAPI to mount the `dist/` directory as static files.

---

## 4. Docker Containerization

The repository includes standard containerization support.

### 4.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies for OpenCV and PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

RUN mkdir -p uploads exports

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.3 Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./movie_preproduction.db
      - CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
    volumes:
      - backend_data:/app/exports
      - backend_uploads:/app/uploads

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  backend_data:
  backend_uploads:
```

Launch the entire stack with:
```bash
docker-compose up --build -d
```

---

## 5. Troubleshooting & FAQ

### 5.1 Hugging Face Model Download Timeout
*Problem*: Downloading `dslim/bert-base-NER` hangs on slow internet connections.
*Solution*: The model is automatically cached locally under `~/.cache/huggingface/hub/`. If offline, set `HF_HUB_OFFLINE=1` in your environment after initial download.

### 5.2 SQLite Concurrency & File Locks
*Problem*: `database is locked` error during rapid concurrent writes.
*Solution*: For high-throughput multi-user production, switch `DATABASE_URL` in `.env` to PostgreSQL:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/movie_preprod_db"
```

### 5.3 PDF Font Rendering in ReportLab
*Problem*: Custom fonts missing on minimal Linux distributions.
*Solution*: ReportLab uses standard Type 1 fonts (Helvetica, Times, Courier) by default, requiring no external font installation.
