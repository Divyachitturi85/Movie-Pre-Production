# System Architecture & Technical Specifications

This document outlines the software architecture, data flow, pipeline stages, and design patterns of the **AI-Powered Movie Pre-Production Planning & Production Management System**.

---

## 1. High-Level Architecture Diagram

```
+--------------------------------------------------------------------------------+
|                                FRONTEND (React 18 + Vite)                      |
|  - Dashboard           - Script Viewer       - Stripboard (Movie Magic Style)  |
|  - Upload & OCR        - Script Breakdown    - Budget Ledger (ATL/BTL)         |
|  - Cast & Characters   - Locations & Sets    - Call Sheets (StudioBinder Style)|
|  - Production Elements - OR-Tools Schedule   - Callback Letters & Export ZIP   |
+---------------------------------------+----------------------------------------+
                                        | HTTP REST (JSON / Multipart / Streams)
                                        v
+--------------------------------------------------------------------------------+
|                             BACKEND (FastAPI / Python 3.11)                    |
|                                                                                |
|  API Layer:                                                                    |
|    /api/projects   /api/script   /api/analyze   /api/schedule   /api/budget    |
|    /api/call-sheets   /api/callbacks   /api/reports   /api/explainability      |
|                                                                                |
|  Service Layer:                                                                |
|    +--------------------+  +--------------------+  +-------------------------+ |
|    | PDFService         |  | ScriptParser       |  | SpacyService            | |
|    | (PyMuPDF/PaddleOCR)|  | (Screenplay Regex) |  | (en_core_web_sm)        | |
|    +--------------------+  +--------------------+  +-------------------------+ |
|    +--------------------+  +--------------------+  +-------------------------+ |
|    | NLPService         |  | ComplexityService  |  | SchedulerService        | |
|    | (BERT-NER + Rules) |  | (Multi-factor)     |  | (Google OR-Tools CP-SAT)| |
|    +--------------------+  +--------------------+  +-------------------------+ |
|    +--------------------+  +--------------------+  +-------------------------+ |
|    | BudgetService      |  | CallSheetService   |  | CallbackService         | |
|    | (Chart of Accounts)|  | (Daily Logistics)  |  | (Audition Letters)      | |
|    +--------------------+  +--------------------+  +-------------------------+ |
|    +-------------------------------------------------------------------------+ |
|    | DocumentService (ReportLab PDF, OpenPyXL XLSX, Python-docx, ZIP Export) | |
|    +-------------------------------------------------------------------------+ |
|                                                                                |
|  Data Layer (SQLAlchemy 2.0 ORM):                                              |
|    SQLite (Default local zero-config) / PostgreSQL (via DATABASE_URL in .env)  |
+--------------------------------------------------------------------------------+
```

---

## 2. Pipeline Execution Flow

1. **Upload & Quality Assessment**:
   The user uploads a movie script PDF. `PDFService` uses `PyMuPDF` to extract text and calculates character density, printable ratio, and scene header presence. If the text quality metric is $< 0.35$ (indicating an image-only or scanned PDF), it automatically activates `PaddleOCR`, renders pages at 150 DPI, extracts text lines, and computes confidence scores.
2. **Grammar & Slugline Parsing**:
   `ScriptParser` normalizes line breaks, detects scene headings (`INT.`, `EXT.`, `INT./EXT.`, `I/E.`), separates dialogue from action blocks, computes estimated pages (1 page = 54 lines), and calculates baseline shooting minutes.
3. **Multi-Model NLP Extraction**:
   Each parsed scene is processed by `NLPService`, which executes:
   - `SpacyService` for sentence segmentation and noun chunk discovery.
   - `Hugging Face Transformers` (`dslim/bert-base-NER`) for token classification.
   - Domain-specific regular expressions for Props, Costumes, Vehicles, Weapons, Animals, and VFX/SFX.
   - Specification engine inferring camera and lighting equipment packages.
   - Generates transparency records stored in `AIExplainabilityRecord`.
4. **Complexity Scoring**:
   `ComplexityService` assigns a weighted numerical score (1.0 to 10.0) and assigns a tier:
   - `LOW`: Controlled interior daytime dialogue.
   - `MEDIUM`: Multiple actors, prop interactions, outdoor daytime.
   - `HIGH`: Night exterior, complex lighting, vehicles, or physical stunts.
   - `VERY HIGH`: Massive cast, pyrotechnics, weapons, VFX/CGI sequences.
5. **Mathematical Scheduling**:
   `SchedulerService` loads all scenes and builds a Google OR-Tools CP-SAT model. It assigns binary variables `scene_day[s, d]`, enforces daily 10-hour limits, minimizes total days and company moves, and produces an optimal shooting schedule.
6. **Budget Formulation**:
   `BudgetService` generates an industry-standard Above-The-Line and Below-The-Line chart of accounts based on shoot days and cast size, dynamically calculating subtotal, 10% contingency, and 8% taxes.
7. **Document Generation**:
   `DocumentService` builds downloadable PDFs (ReportLab), XLSX workbooks (OpenPyXL), and packages all 11 production artifacts into a single `.zip` archive.
