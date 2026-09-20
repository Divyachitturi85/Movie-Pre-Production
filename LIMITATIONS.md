# System Limitations, Edge Cases & Future Roadmap

For academic integrity and production evaluation, this document details the known technical boundaries, edge cases, and architectural constraints of the **AI-Powered Movie Pre-Production Planning & Production Management System**, alongside proposed future enhancements.

---

## 1. Screenplay Formatting & Structural Variances

### 1.1 Non-Standard Margins & Indentation
- **Constraint**: Screenplay industry standards dictate strict indentations (e.g., Character cues at 3.7 inches, Dialogue at 2.5 inches). Non-compliant scripts created in general-purpose word processors (Microsoft Word, Google Docs) without screenplay templates may cause character cues to be parsed as action lines.
- **Mitigation**: The system incorporates fallback regex patterns looking for uppercase tokens followed immediately by indented dialogue blocks.

### 1.2 Multi-Column & Dual Dialogue
- **Constraint**: When two characters speak simultaneously, screenplays place dialogue blocks side-by-side in two parallel columns. Linear text extraction via PyMuPDF may interleave the text horizontally (e.g., reading line 1 of Character A, then line 1 of Character B).
- **Mitigation**: PyMuPDF's column-aware sorting extracts contiguous bounding boxes, but highly complex multi-column overlap can occasionally require manual line-break review in the Script Viewer.

### 1.3 Shooting Script Revision Marks
- **Constraint**: Production shooting scripts frequently include revision asterisks (`*`) in the right-hand margin and colored page notations (e.g., `PINK REVISED PAGES - 10/12/2025`).
- **Mitigation**: Pre-filtering strip rules eliminate trailing margin asterisks and revision headers prior to passing text to the NLP pipeline.

---

## 2. OCR Fallback on Physical Scans

### 2.1 Resolution & Skew Limitations
- **Constraint**: Physical scans under 150 DPI or with skew angles $> 15^\circ$ experience degraded OCR character accuracy, particularly misidentifying punctuation (`.` as `,`, leading to corrupted sluglines).
- **Mitigation**: PaddleOCR incorporates automatic text orientation detection (`use_angle_cls=True`), but scanning at 300 DPI remains recommended for optimal fidelity.

### 2.2 Handwritten Director Notes & Markups
- **Constraint**: Scanned scripts containing handwritten pen annotations in margins or across dialogue lines can inject noisy non-lexical tokens into the text stream.
- **Mitigation**: The Text Quality Scorer evaluates printable character density and flags scripts with high noise ratios.

---

## 3. NLP Boundary & Polysemy Ambiguities

### 3.1 Lexical Polysemy (Contextual Word Sense)
- **Constraint**: Screenplay nouns can have radically different meanings depending on syntactic context:
  - `Glasses`: Eyewear costume accessory vs. bar drinking glassware.
  - `Ring`: Jewelry hand prop vs. telephone sound effect.
  - `Suit`: Protective spacesuit vs. business wardrobe vs. legal lawsuit.
  - `Shot`: Camera angle direction vs. firearm gunshot sound effect vs. liquor shot prop.
- **Mitigation**: The system leverages spaCy's dependency parser to inspect the governing head verb and prepositional modifiers (e.g., `pours a shot` $\rightarrow$ Prop; `hears a shot` $\rightarrow$ Sound Effect).

### 3.2 Metaphorical & Non-Physical Narrative Descriptions
- **Constraint**: Screenwriters often use evocative literary language that does not correspond to physical production assets (e.g., *"Her eyes carry the weight of a thousand dying suns"*).
- **Mitigation**: The Hugging Face BERT NER model flags entities with confidence scores, and items scoring below the 0.70 threshold are filtered out before reaching the Production Elements database.

---

## 4. Computation, Latency & Hardware Dependencies

### 4.1 CPU vs. GPU Inference Latency
- **Constraint**: Running PyTorch with Hugging Face `dslim/bert-base-NER` on a CPU takes approximately 1.5 to 3.0 seconds per script page. On a standard 120-page feature film, CPU parsing can require 3 to 6 minutes.
- **Mitigation**: The pipeline caches parsed results in SQLite/PostgreSQL, ensuring parsing occurs only once per script upload. GPU acceleration (CUDA) is automatically detected and leveraged when available.

### 4.2 Mathematical Optimization Scalability (Google OR-Tools)
- **Constraint**: The scheduling problem is NP-Hard. For feature productions with $>200$ scenes, searching for the globally optimal schedule under strict constraints can lead to combinatorial explosion.
- **Mitigation**: The CP-SAT solver includes a 30-second execution time limit (`max_time_in_seconds=30.0`), returning the best feasible solution discovered if the global optimum is not proven within that window.

---

## 5. Union & Guild Labor Compliance Boundaries

### 5.1 SAG-AFTRA & IATSE Labor Rules
- **Constraint**: Professional productions must abide by strict union regulations, such as SAG-AFTRA 12-hour turnaround times, "Day-out-of-Days" (DOOD) consecutive employment rules, and IATSE meal penalty thresholds.
- **Mitigation**: The scheduler models daily 12-hour caps and minimizes cast idle gaps; however, specialized local collective bargaining agreements (CBAs) still require review by an Assistant Director (1st AD) or Production Manager.

---

## 6. Future Technical Roadmap

1. **Multimodal Script Analysis**:
   - Integrating Vision-Language Models (e.g. Gemini 1.5 Pro / GPT-4o) to simultaneously parse screenplay text alongside embedded concept art and storyboard sketches.
2. **Real-Time Weather API Integration**:
   - Connecting daily call sheets directly to live meteorological APIs (OpenWeatherMap / NOAA) based on location GPS coordinates.
3. **Automated AI Storyboard Generation**:
   - Generating 4-panel visual storyboards for high-complexity scenes using Diffusion models directly from parsed action descriptions.
4. **Multi-User Collaborative Stripboard**:
   - WebSocket-enabled live multi-user editing for 1st ADs and Line Producers with change tracking and conflict resolution.
