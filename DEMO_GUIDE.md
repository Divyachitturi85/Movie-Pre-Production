# Evaluator & Demonstration Guide

This guide provides step-by-step instructions for college professors, thesis evaluators, industry supervisors, and recruiters to test, demonstrate, and verify every module of the **AI-Powered Movie Pre-Production Planning & Production Management System**.

---

## 1. Quick Start: Launching the Application

### Step 1: Start the FastAPI Backend
Open a terminal in the project root:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Verify backend health: `http://127.0.0.1:8000/api/health` $\rightarrow$ returns `{"status":"healthy"}`.
- Swagger API Docs: `http://127.0.0.1:8000/docs`.

### Step 2: Start the Vite React Frontend
Open a second terminal:
```bash
cd frontend
npm run dev
```
- Open your browser to: **`http://localhost:5173`**.

---

## 2. Demonstration Path A: 1-Click "Project Aurora" (Recommended)

To evaluate the system immediately without waiting for an external PDF upload, use the built-in demonstration project **"Project Aurora"** (a 9-scene sci-fi thriller screenplay).

### Walkthrough Steps:

1. **Initialize Demo Data**:
   - In the left sidebar or top banner, click the blue **"Load Demo Project"** button.
   - The backend automatically seeds 9 scenes, 6 characters, 5 filming locations, 30+ categorized production elements, an optimized schedule, a full budget ledger, call sheets, and callback letters into the SQLite database.

2. **Executive Dashboard (`/dashboard`)**:
   - Observe key performance indicators: Total Scenes (9), Estimated Shoot Days (4), Grand Total Budget ($2,849,580), and High-Risk Scenes.
   - Inspect the interactive Recharts graphs: Scenes by Location distribution, Character Dialogue frequency, and Complexity breakdown pie chart.

3. **Courier Prime Script Viewer (`/script-viewer`)**:
   - View the formatted screenplay rendered in authentic industry **Courier Prime 12pt** typography with exact margin alignments.
   - Use the scene jump dropdown to leap instantly to Scene 4 ("INT. HYDROPONICS LAB - NIGHT") or Scene 7 ("EXT. SURFACE OF PROXIMA B - DAY").

4. **StudioBinder-Style Script Breakdown (`/breakdown`)**:
   - Review scene breakdown cards itemizing every production element detected by AI.
   - Observe color-coded department tags:
     - 🟣 **VFX** (Atmospheric Distortion, Plasma Discharge)
     - 🔴 **Props** (Handheld Scanner, Cryo-Canister)
     - 🔵 **Costumes** (Pressurized EVA Suit)
     - 🟡 **Vehicles** (All-Terrain Exploration Rover)

5. **Cast & Character Management (`/characters`)**:
   - View cast statistics: Dialogue line counts, total scenes, and estimated on-set days.
   - Click the **Edit** icon next to *DR. ELENA VANCE* to update actor attachment details or talent agent contact info.

6. **Filming Locations & Logistics (`/locations`)**:
   - View interior vs. exterior locations.
   - Check company move logistics and estimated daily rental fees.

7. **Production Elements Breakdown (`/elements`)**:
   - Filter items across department tabs: *Props, Costumes, Vehicles, Equipment, VFX, SFX, Weapons, Animals*.
   - Click **"+ Add Custom Element"** to manually insert a new production asset and verify dynamic state updates.

8. **Google OR-Tools CP-SAT Schedule Optimizer (`/schedule`)**:
   - View the mathematically optimal 4-day shooting schedule.
   - Notice how scenes in the same location (e.g., *HYDROPONICS LAB*) are grouped consecutively to minimize expensive company moves.
   - Adjust the **Max Hours Per Day** slider (e.g. from 12 hours to 10 hours) and click **"Re-Optimize Schedule"** to watch the CP-SAT solver recompute in real-time.

9. **Movie Magic-Style Stripboard (`/stripboard`)**:
   - Review the industry-standard color-coded production strips:
     - 🟡 **Yellow Strip**: Exterior Day
     - ⚪ **White Strip**: Interior Day
     - 🟢 **Green Strip**: Exterior Night
     - 🔵 **Blue Strip**: Interior Night
   - Black separator strips demarcate **END OF DAY** transitions with cumulative day hours.

10. **Budgeting Ledger (`/budget`)**:
    - View Above-the-Line (ATL: Director, Producers, Cast) and Below-the-Line (BTL: Camera, Grip, Electric, VFX) line items.
    - Test dynamic recalculation: Modify the Director fee or Daily Location fee, and observe the **10% Contingency** and **8% Tax** automatically recalculate in real-time.

11. **StudioBinder-Style Call Sheets (`/call-sheets`)**:
    - View daily call sheets containing general crew call (07:00), first shot call (08:00), catering meal breaks, and assigned emergency hospital directives.
    - Click **"Download Call Sheet (PDF)"** to generate and inspect a crisp, printable ReportLab PDF.

12. **Actor Audition Callback Studio (`/callbacks`)**:
    - View personalized callback appointment letters generated for auditioning talent.
    - Click **"Generate Single Callback"** or **"Generate All Callbacks"**.
    - Click **"Download Letter (PDF)"** to verify the formal casting appointment letter.

13. **Executive Production Report & 11-Artifact ZIP (`/reports`)**:
    - Read the comprehensive pre-production executive briefing.
    - Click **"Download Complete Pre-Production Package (.ZIP)"** to download all 11 generated production artifacts (PDFs, Excel XLS ledgers, Word DOCX documents) in a single unified archive.

14. **Academic Explainability Audit (`/explainability`)**:
    - Review the algorithmic transparency audit trail for every classified element.
    - Inspect model names (`dslim/bert-base-NER`, `en_core_web_sm`), statistical confidence scores, and syntactic rationale.

---

## 3. Demonstration Path B: Ingesting a Custom PDF Screenplay

To demonstrate real-time ingestion of an arbitrary PDF:

1. Navigate to **Upload Script** (`/upload`).
2. Drag and drop any screenplay PDF (or use the sample PDF located at `backend/demo_data/sample_script.pdf`).
3. Observe the real-time processing metrics:
   - **Text Quality Meter**: Measures printable character density.
   - **OCR Confidence**: Shows 100% for digital PDFs, or displays PaddleOCR confidence for scanned documents.
4. Click **"Execute AI Pre-Production Pipeline"**:
   - Watch the sequential progress indicators: PDF Extraction $\rightarrow$ Slugline Parsing $\rightarrow$ spaCy Tagging $\rightarrow$ Hugging Face NER $\rightarrow$ OR-Tools Optimization $\rightarrow$ Budget Generation.
5. Upon completion, navigate through the dashboard to inspect the newly extracted data.

---

## 4. Key Talking Points for Project Defense / Viva Voce

| Question / Topic | Model Answer |
| :--- | :--- |
| **Which actual AI models are used vs. inspired systems?** | *We implement real AI and optimization engines: PyMuPDF + PaddleOCR for ingestion, spaCy (`en_core_web_sm`) for syntactic parsing, Hugging Face (`dslim/bert-base-NER`) for entity classification, and Google OR-Tools CP-SAT for mathematical scheduling. Systems like Movie Magic, StudioBinder, and Celtx represent industry workflows whose layouts and standards we emulate.* |
| **How does the scheduling optimizer work?** | *It is a Constraint Satisfaction & Optimization problem modeled with Google OR-Tools CP-SAT. Decision variables assign scenes to shoot days subject to daily hour limits ($H_{max} \le 12$), while minimizing an objective function that penalizes location company moves and cast idle gaps.* |
| **How does the system ensure explainability?** | *Every AI classification generates an `AIExplainabilityRecord` stored in SQLite, recording the exact model used, the confidence score, the source text excerpt, and the linguistic rule or syntactic dependency that triggered the decision.* |
| **Can the system handle physical scanned PDFs?** | *Yes. If PyMuPDF detects a text density below 30 characters per page, it automatically routes page rasters through PaddleOCR with angle classification at 150 DPI to extract raw screenplay text.* |
