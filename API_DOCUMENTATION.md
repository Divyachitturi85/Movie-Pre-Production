# REST API Specification & Endpoint Documentation

The backend service is powered by **FastAPI** with automatic OpenAPI documentation available at `/docs` and `/redoc`.

Base URL: `http://localhost:8000/api`

---

## 1. Projects API (`/api/projects`)

### `GET /api/projects`
- **Description**: Returns all production projects with summary metrics.
- **Response**: Array of `ProjectResponse` objects.

### `POST /api/projects`
- **Description**: Initializes a new production project.
- **Body**: `{ "name": string, "description": string, "genre": string, "director": string, "producer": string }`
- **Response**: `ProjectResponse` (HTTP 201).

### `GET /api/projects/{id}`
- **Description**: Returns project metadata and aggregate scene, cast, location, schedule, and budget metrics.

### `POST /api/projects/demo/load`
- **Description**: 1-Click demo loader that initializes "Project Aurora" with full pre-production data.

### `DELETE /api/projects/{id}`
- **Description**: Cascading delete for a project and all associated data.

---

## 2. Scripts & Ingestion API (`/api/projects/{id}/script`)

### `POST /api/projects/{id}/script/upload`
- **Description**: Uploads a `.pdf` movie script, assesses text quality, invokes PaddleOCR if scanned, and parses scenes.
- **Content-Type**: `multipart/form-data` (`file: UploadFile`)
- **Response**: `ScriptResponse` with extraction method, OCR confidence, and page counts.

### `GET /api/projects/{id}/script`
- **Description**: Retrieves script metadata, raw extracted text, and cleaned screenplay text.

### `POST /api/projects/{id}/script/parse`
- **Description**: Re-parses scenes from custom screenplay text.

---

## 3. Analysis & Breakdown API (`/api/projects/{id}`)

### `POST /api/projects/{id}/analyze`
- **Description**: Triggers full Hugging Face BERT-NER, spaCy linguistic analysis, and scene complexity scoring.
- **Response**: Summary of extracted characters, locations, and production elements.

### `GET /api/projects/{id}/scenes`
- **Description**: Lists all parsed scenes with sluglines, duration, complexity level, and tagged elements.

### `GET /api/projects/{id}/characters`
- **Description**: Lists identified characters, scene counts, dialogue counts, and shooting days.

### `PUT /api/projects/{id}/characters/{char_id}`
- **Description**: Updates character role tier, costume notes, or makeup notes.

### `GET /api/projects/{id}/locations`
- **Description**: Lists locations with INT/EXT, day/night scene counts, and company move requirements.

### `GET /api/projects/{id}/elements`
- **Description**: Returns categorized production elements (Props, Costumes, Vehicles, Equipment, VFX, SFX, Weapons).
- **Query Params**: `?category=PROP`

---

## 4. Scheduling & Stripboard API (`/api/projects/{id}`)

### `POST /api/projects/{id}/schedule/optimize`
- **Description**: Executes Google OR-Tools CP-SAT scheduling optimization.
- **Body**: `{ "max_daily_hours": 10.0, "prioritize_locations": true }`
- **Response**: Complete day-by-day shooting schedule with start times, company moves, and solver statistics.

### `GET /api/projects/{id}/schedule`
- **Description**: Retrieves existing shooting schedule.

### `GET /api/projects/{id}/stripboard`
- **Description**: Returns Movie Magic Scheduling-compatible color-coded stripboard data.

---

## 5. Budget API (`/api/projects/{id}/budget`)

### `GET /api/projects/{id}/budget`
- **Description**: Retrieves current budget ledger with Above/Below-the-Line items.

### `POST /api/projects/{id}/budget/generate`
- **Description**: Generates an initial budget based on shoot days and cast size.

### `PUT /api/projects/{id}/budget/items`
- **Description**: Updates line item quantities, rates, or days with live recalculation.

---

## 6. Documents & Exports API (`/api/projects/{id}`)

### `POST /api/projects/{id}/call-sheets/generate`
- **Description**: Generates StudioBinder-style daily call sheets for all shooting days.

### `GET /api/projects/{id}/call-sheets`
- **Description**: Lists daily call sheets.

### `GET /api/projects/{id}/call-sheets/{sheet_id}/export/{format}`
- **Description**: Downloads call sheet in `pdf` or `docx` format.

### `POST /api/projects/{id}/callbacks/generate`
- **Description**: Generates audition callback letters for all identified characters.

### `GET /api/projects/{id}/callbacks/export/pdf`
- **Description**: Downloads compiled PDF of all callback letters.

### `GET /api/projects/{id}/export/package`
- **Description**: Downloads the Complete Pre-Production Package as a `.zip` archive containing all 11 production documents and JSON database export.
