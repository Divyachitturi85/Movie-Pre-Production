# AI-Powered Movie Pre-Production Planning & Production Management System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-4285F4?logo=google&logoColor=white)](https://developers.google.com/optimization)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![spaCy](https://img.shields.io/badge/spaCy-Linguistic%20NLP-09A3D5?logo=spacy&logoColor=white)](https://spacy.io/)

An academic and production-grade software system that ingests a screenplay PDF, performs AI/NLP/OCR extraction, scores scene complexity, optimizes physical shooting schedules using **Google OR-Tools CP-SAT**, calculates configurable film budgets, and exports comprehensive production packages including **StudioBinder-style Call Sheets**, **Audition Callback Letters**, **Movie Magic-style Stripboards**, and **Excel data ledgers**.

---

## Key Features

1. **Intelligent PDF Ingestion & OCR Fallback**:
   - High-throughput PDF extraction via `PyMuPDF`.
   - Automated text quality heuristic assessing alphanumeric density, character count, and formatting.
   - Transparent fallback to `PaddleOCR` with page rendering and confidence tracking if scanned documents are uploaded.
2. **Screenplay Grammar & Slugline Parsing**:
   - Recognizes standard sluglines (`INT.`, `EXT.`, `INT./EXT.`), scene numbers, and day/night temporal indicators.
   - Detects character cues, parentheticals, dialogues, actions, and transitions.
   - Estimates standard 1/8ths of a page and projected shooting durations.
3. **Multi-Model NLP Breakdown Engine**:
   - **spaCy (`en_core_web_sm`)**: Sentence segmentation, tokenization, POS tagging, and noun chunk extraction.
   - **Hugging Face Transformers (`dslim/bert-base-NER`)**: Token classification identifying characters, locations, props, costumes, vehicles, equipment, weapons, and VFX/SFX.
   - Production specification engine matching camera, sound, and lighting packages based on scene parameters.
4. **Weighted Scene Complexity Scoring**:
   - Multi-factor algorithm evaluating cast density, exterior exposure, night shoot setups, stunts, and CGI.
   - Classifies scenes into `LOW`, `MEDIUM`, `HIGH`, and `VERY HIGH` with factor breakdowns.
5. **Google OR-Tools CP-SAT Schedule Optimization**:
   - Formulates a rigorous integer programming model with decision variables, daily hour constraints, setup buffers, and location clustering.
   - Mathematically minimizes total shooting days, company moves, and cast idle gaps.
6. **Movie Magic & StudioBinder Inspired Workflows**:
   - **Stripboard**: Industry standard color coding (EXT. DAY = Yellow, INT. DAY = White, EXT. NIGHT = Green, INT. NIGHT = Blue).
   - **Budget Engine**: Configurable Above-The-Line (ATL) and Below-The-Line (BTL) chart of accounts with live recalculation of contingency and taxes.
   - **Call Sheets**: StudioBinder-style daily call sheets with scene lists, talent call times, crew departments, and hospital contacts.
   - **Audition Callback Letters**: Official actor callback invitations with scheduled slots, sides references, and preparation instructions.
7. **Complete 11-Artifact Pre-Production Package (.ZIP)**:
   - Compiles downloadable PDFs (Breakdown, Stripboard, Call Sheets, Callback Letters, Report), XLSX workbooks (Scenes, Cast, Locations, Elements, Schedule, Budget), and `complete_project.json`.
8. **1-Click Demo Mode ("Project Aurora")**:
   - Instant demonstration with a built-in 9-scene sci-fi action screenplay without requiring an external PDF upload.

---

## System Architecture

```
Movie/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── core/            # Config & database setup
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # AI, NLP, OCR, OR-Tools, and Document services
│   │   └── main.py          # Application entry point
│   ├── tests/               # Pytest automated test suite
│   ├── demo_data/           # Built-in sample PDF scripts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── layouts/         # Navigation & AppLayout
│   │   ├── pages/           # 14 Full-featured pages
│   │   ├── services/        # Axios API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── docs/                    # Architectural and algorithmic guides
```

---

## Quickstart & Local Setup

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend web application will open at `http://localhost:5173`.

### 3. Automated Tests
```bash
cd backend
python -m pytest tests -v
```

---

## Distinguishing Implemented Technologies vs Inspired Workflows

- **PaddleOCR**: *Directly Implemented* for optical character recognition of scanned script pages.
- **spaCy**: *Directly Implemented* (`en_core_web_sm`) for linguistic tokenization and entity candidates.
- **Hugging Face Transformers**: *Directly Implemented* (`dslim/bert-base-NER`) for semantic entity classification.
- **Google OR-Tools**: *Directly Implemented* (`ortools.sat.python.cp_model`) for constraint programming schedule optimization.
- **Movie Magic Scheduling / Budgeting**: *Workflow Inspired* — implements compatible stripboard colors and A-T-L/B-T-L chart of accounts without claiming proprietary API integration.
- **StudioBinder**: *Workflow Inspired* — implements breakdown sheet structures and daily call sheet standards.
- **Celtx**: *Workflow Inspired* — implements screenplay reading formats and script asset tagging.
