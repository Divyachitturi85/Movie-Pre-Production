# AI Tools, Machine Learning Models & Inspired Workflows

This document clarifies how AI, NLP, OCR, and Optimization algorithms are implemented, explicitly distinguishing **direct library integrations** from **industry-inspired workflows**.

---

## 1. Summary Matrix

| Technology / Workflow | Implementation Type | Purpose in System | Fallback Mechanism |
| :--- | :--- | :--- | :--- |
| **PaddleOCR** | **Direct Integration** | Optical character recognition on scanned screenplay PDFs | Computer vision text extraction with confidence tracking |
| **spaCy (`en_core_web_sm`)** | **Direct Integration** | Sentence segmentation, tokenization, POS tagging, noun chunks | Rule-based regex linguistic tokenizer |
| **Hugging Face (`dslim/bert-base-NER`)** | **Direct Integration** | Token classification & Named Entity Recognition (NER) | Screenplay dialogue cue heuristics |
| **Google OR-Tools (CP-SAT)** | **Direct Integration** | Mathematical constraint programming for shooting schedules | Location-clustering greedy heuristic |
| **Movie Magic Scheduling** | **Inspired Workflow** | Film industry standard color-coded stripboard layout | N/A (Fully implemented UI/PDF) |
| **Movie Magic Budgeting** | **Inspired Workflow** | Above-the-Line & Below-the-Line chart of accounts structure | N/A (Configurable formula ledger) |
| **StudioBinder** | **Inspired Workflow** | Scene breakdown sheets & daily call sheet logistics | N/A (Fully implemented UI/PDF/DOCX) |
| **Celtx** | **Inspired Workflow** | Authentic screenplay reading format & slugline segmentation | N/A (Screenplay CSS & font rendering) |

---

## 2. Direct AI Implementations

### PaddleOCR
- **Role**: Fallback OCR pipeline for scanned, photographed, or non-digital PDF scripts.
- **How it works**:
  1. `PDFService.assess_text_quality()` evaluates text length, alphanumeric ratio, and screenplay keywords.
  2. If quality score is $< 0.35$, PyMuPDF renders PDF pages as 150 DPI RGB raster images.
  3. `PaddleOCR` (using pre-trained detection and recognition models) extracts bounding boxes and text lines.
  4. Returns cleaned text along with an average OCR confidence score logged in the database.

### spaCy (`en_core_web_sm`)
- **Role**: Linguistic parsing and structural entity discovery.
- **How it works**:
  1. Breaks screenplay prose into sentences and noun chunks.
  2. Identifies syntactic noun phrases that represent physical objects, props, and garments (e.g., "a silver briefcase", "a glowing quantum cylinder").
  3. Labels linguistic entities (`PERSON`, `GPE`, `LOC`, `FAC`, `PRODUCT`).

### Hugging Face Transformers (`dslim/bert-base-NER`)
- **Role**: Deep learning contextual Named Entity Recognition.
- **How it works**:
  1. Screenplay text passages are passed to the BERT NER pipeline.
  2. The transformer recognizes entity spans (`PER` for characters, `LOC` for settings).
  3. Complemented by screenplay domain regex classifiers to categorize specialized assets into **Props, Costumes, Vehicles, Weapons, Animals, and VFX/SFX**.
  4. Records every decision in the `ai_explainability_records` table with model name and confidence.

### Google OR-Tools (CP-SAT Solver)
- **Role**: Combinatorial constraint optimization for production shooting schedules.
- **How it works**:
  1. Implements a Constraint Programming model using the SAT solver (`cp_model.CpSolver`).
  2. Assigns scenes to shooting days subject to strict daily shooting hour limits (default 10h) and setup time buffers.
  3. Minimizes a weighted objective function:
     $$\min \left( 1000 \cdot \sum \text{DayActive} + 100 \cdot \sum \text{LocationOccurrences} + 10 \cdot \sum \text{CastDays} \right)$$
  4. Guarantees consecutive day allocation, clusters shared locations to eliminate company moves, and produces optimal sequences.

---

## 3. Workflows Inspired by Industry Standards

### Movie Magic Scheduling Concepts
- **Industry Convention**: Film assistant directors use color-coded strips on a physical or digital board to represent scenes.
- **Our Implementation**: We implement the exact standard color hierarchy:
  - **EXT. DAY** = Yellow (`#FEF08A`)
  - **INT. DAY** = White (`#FFFFFF`)
  - **EXT. NIGHT** = Green (`#BBF7D0`)
  - **INT. NIGHT** = Blue (`#BFDBFE`)
- *Disclaimer*: We do not claim an official API integration with Movie Magic. Our application generates compatible stripboard views and downloadable PDFs conforming to industry standards.

### Movie Magic Budgeting Concepts
- **Industry Convention**: Film budgets are organized into Above-The-Line (ATL: Director, Producers, Cast, Screenplay) and Below-The-Line (BTL: Camera, Lighting, Sound, Art, Locations, Catering, VFX, Post-Production).
- **Our Implementation**: We provide an interactive, editable financial ledger using standard four-digit account codes (`1100`, `1400`, `2000`, `2600`) with dynamic calculation of subtotals, contingency (10%), and taxes (8%).
- *Disclaimer*: Illustrative planning estimates — user configurable. No official connection to Entertainment Partners or proprietary software.

### StudioBinder Concepts
- **Industry Convention**: Breakdown sheets that tag script elements with distinct colors (Cast in Blue, Props in Amber, Wardrobe in Purple, VFX in Red) and formatted daily call sheets with hospital locations and meal breaks.
- **Our Implementation**: Fully realized interactive breakdown cards with color-coded tags and automated daily call sheets exportable to PDF and DOCX.
