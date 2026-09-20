# AI Prompts, NLP Heuristics & Classification Rules

This document details the exact linguistic patterns, NLP pipelines, token classification schemes, entity-extraction heuristics, and explainability prompt templates utilized throughout the **AI-Powered Movie Pre-Production Planning & Production Management System**.

---

## 1. Pipeline Overview & Model Hierarchy

The system does not rely on opaque monolithic LLM generation for mission-critical pre-production data. Instead, it utilizes a deterministic, reproducible, multi-layered NLP and machine learning hierarchy:

```
                      Raw Screenplay Text / Scanned PDF
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        PyMuPDF Text Stream                      PaddleOCR Engine
    (Clean Digital Scripts)                   (Scanned Physical Pages)
                 └───────────────────┬───────────────────┘
                                     ▼
                     Regex Screenplay State Machine
                (Sluglines, Action, Characters, Dialogue)
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
           spaCy Parser                         Hugging Face NER
        (`en_core_web_sm`)                    (`dslim/bert-base-NER`)
    • Part-of-Speech Tagging                • Token Classification
    • Dependency Parsing                    • PER / LOC / ORG / MISC
    • Noun Chunks Extraction                • Sub-word Aggregation
                 └───────────────────┬───────────────────┘
                                     ▼
                Domain Knowledge Heuristic Classifier
           (Props, Costumes, Vehicles, Equipment, VFX, SFX)
                                     │
                                     ▼
                 Multi-Factor Complexity Scoring Engine
                  (Weights: Cast, VFX, Stunts, Lighting)
```

---

## 2. Screenplay Parsing Heuristics & Regular Expressions

Screenplays follow strict industry typographical standards (Courier 12pt, specific margins, capitalized sluglines). The system applies compiled state-machine regular expressions to segment script blocks:

### 2.1 Scene Heading (Slugline) Detection
```python
SLUGLINE_PATTERN = r'^(?:(?:SCENE\s+\d+[:.\s]*)?(INT\.|EXT\.|INT\./EXT\.|I/E\.)\s+([A-Z0-9\s\-\'\/]+?)(?:\s+-\s+(DAY|NIGHT|DUSK|DAWN|CONTINUOUS|LATER|SUNSET|SUNRISE))?(?:\s+#\d+#)?)$'
```
- **Captures**:
  - Group 1: Setting type (`INT.`, `EXT.`, `INT./EXT.`, `I/E.`)
  - Group 2: Scene location name (e.g., `MISSION CONTROL CENTER`, `SUBWAY PLATFORM`)
  - Group 3: Time of day (`DAY`, `NIGHT`, `DUSK`, `DAWN`, `CONTINUOUS`)

### 2.2 Character Speaking Cue Detection
```python
CHARACTER_CUE_PATTERN = r'^[ \t]{10,35}([A-Z0-9\s\.\'\-]+(?:\s*\(.*?\))?)$'
```
- **Rules**:
  - Uppercase string preceded by screenplay indentation (10–35 spaces or centered).
  - Handles parenthetical actor designations: `SARAH (O.S.)`, `MARCUS (V.O.)`, `OFFICER (CONT'D)`.
  - Filters out common script false positives: `THE END`, `FADE OUT:`, `CUT TO:`, `DISSOLVE TO:`.

### 2.3 Parenthetical Direction Detection
```python
PARENTHETICAL_PATTERN = r'^\s*\((.*?)\)\s*$'
```
- **Captures**: Acting notes before or within dialogue (e.g., `(whispering)`, `(pointing to monitor)`).

### 2.4 Transition Detection
```python
TRANSITION_PATTERN = r'^(FADE IN:|FADE OUT\.|CUT TO:|SMASH CUT TO:|MATCH CUT TO:|DISSOLVE TO:|JUMP CUT TO:)$'
```

### 2.5 Page Fraction (1/8ths) Estimation
Standard industry filming speed measures script length in **1/8ths of a page** (8/8 = 1 full page = ~1 minute of screen time).
```python
lines_count = len(scene.action_lines) + len(scene.dialogue_lines)
# 1 standard script page = ~54 lines of Courier 12pt
# 1/8th of a page = ~6.75 lines
eighths = max(1, round(lines_count / 6.75))
page_fraction = f"{eighths}/8" if eighths < 8 else f"{eighths // 8} {eighths % 8}/8"
```

---

## 3. spaCy Linguistic Analysis Pipeline

Model: `en_core_web_sm` (Linguistic parsing and noun chunk phrase extraction)

### 3.1 Sentence Segmentation & POS Filtering
To isolate tangible physical items from abstract screenplay narrative:
```python
doc = nlp_spacy(action_text)
candidate_chunks = [
    chunk.text.strip()
    for chunk in doc.noun_chunks
    if not any(token.pos_ in ["PRON", "DET"] for token in chunk.root.children)
    and len(chunk.text.split()) <= 4
]
```

### 3.2 Grammatical Rules for Prop Action Linkage
Verbs governing direct objects often indicate practical hand props:
- Active Verbs: `holds`, `draws`, `aims`, `types`, `opens`, `injects`, `wields`, `ignites`.
- When an active verb directly modifies a noun chunk via a `dobj` dependency tag, that noun chunk is automatically flagged as a **Critical Hand Prop**.

---

## 4. Hugging Face Named Entity Recognition (NER) Pipeline

Model: `dslim/bert-base-NER` (Fine-tuned BERT for CoNLL-2003 Token Classification)

### 4.1 Token Classification Scheme
- `B-PER` / `I-PER`: Cast members, character names, historical figures.
- `B-LOC` / `I-LOC`: Geographic locations, planets, rooms, architectural spots.
- `B-ORG` / `I-ORG`: Military branches, space agencies, corporate institutions.
- `B-MISC` / `I-MISC`: Specialized vehicles, technology classes, weapon systems.

### 4.2 Sub-Word Aggregation & Confidence Thresholding
BERT tokenizes words into WordPiece sub-tokens (e.g., `["Auto", "##loader"]`). The aggregation algorithm:
1. Merges sub-words into contiguous entities.
2. Computes the geometric mean of sub-token probability scores.
3. Discards entities with confidence $< 0.70$.
4. Cross-validates against screenplay character cues to eliminate spurious classifications.

---

## 5. Domain Knowledge Taxonomy & Categorization Rules

Production elements are classified into eight standard film departments using semantic keyword taxonomies combined with regex boundary matching:

### 5.1 Vehicles (`VEHICLE`)
```
Keywords: car, rover, transport, helicopter, jet, spacecraft, truck, motorcycle, van, ambulance, shuttle, boat, ship, submarine, tank, rover, buggy
```

### 5.2 Weapons (`WEAPON`)
```
Keywords: rifle, pistol, gun, blaster, plasma cannon, dagger, knife, sword, grenade, shotgun, taser, revolver, sniper, firearm, warhead
```

### 5.3 Costumes (`COSTUME`)
```
Keywords: spacesuit, helmet, hazmat, uniform, combat armor, tuxedo, wedding dress, cloak, lab coat, tactical vest, boots, gown, disguise
```

### 5.4 Props (`PROP`)
```
Keywords: datapad, scanner, canister, syringe, keys, briefcase, folder, flashlight, radio, communicator, sample, vial, tablet, badge, binoculars, microchip
```

### 5.5 Visual Effects (`VFX`)
```
Keywords: hologram, atmospheric breach, laser beam, disintegrating, cgi creature, energy shield, warp drive, zero gravity, hyperspace, forcefield
```

### 5.6 Sound Effects (`SFX`)
```
Keywords: explosion, blast, siren, hull rupture, gunfire, thunder, sonic boom, screech, earthquake, glass shatter, decompression
```

### 5.7 Camera & Production Equipment (`EQUIPMENT`)
```
Keywords: steadicam, technocrane, drone, underwater housing, anamorphic lens, high-speed camera, dolly, wire rig, gimbal
```

### 5.8 Animals (`ANIMAL`)
```
Keywords: dog, cat, horse, bird, snake, rat, wolf, tiger, falcon, hound, steed
```

---

## 6. Explainability Audit Prompt Template

For academic transparency, every classification produces an `AIExplainabilityRecord` stored in the database. The structured audit schema includes:

```json
{
  "element_name": "Pressurized Containment Canister",
  "category": "PROP",
  "ai_technique": "spaCy Noun Chunk + Domain Heuristic Classifier",
  "model_name": "en_core_web_sm / ProductionTaxonomyRules",
  "confidence_score": 0.94,
  "rationale": "Extracted as direct object noun chunk governed by verb 'secures' in Scene 4 action line. Keyword 'canister' matched Prop taxonomy table with high semantic relevance."
}
```

---

## 7. Actor Audition Callback Letter Generation Template

The system dynamically populates personalized audition letters using director-level audition parameters:

```text
CONFIDENTIAL AUDITION CALLBACK NOTICE
Date: {letter_date}

To: {actor_name}
Represented by: {agent_name} / {agency_name}

RE: Casting for the Role of "{role_name}"
Production Title: "{project_title}"
Production Company: {production_company}

Dear {actor_name},

Thank you for your outstanding initial reading. On behalf of Director {director_name} and our casting department, we are pleased to invite you to a formal callback audition.

AUDITION APPOINTMENT DETAILS:
------------------------------------------------------------
Date & Time: {callback_datetime}
Studio Stage: {audition_location}
Session Type: {session_type} (e.g., Chemistry Read with Lead / Scene Work)
Sides Attached: Scene {assigned_scene_number} (Pages {script_pages})
Preparation Notes: {director_notes}

WARDROBE & GROOMING:
{wardrobe_instructions}

Please confirm receipt and attendance with our casting coordinator within 24 hours.

Warm regards,

{casting_director_name}
Head of Casting
{production_company}
```

All templates are rendered cleanly to screen and exportable as high-fidelity **ReportLab PDFs**.
