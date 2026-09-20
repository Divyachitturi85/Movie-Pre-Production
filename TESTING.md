# Testing Suite & Verification Guide

This document details the automated test suite, verification methodology, and quality assurance procedures for the **AI-Powered Movie Pre-Production Planning & Production Management System**.

---

## 1. Quality Assurance Architecture

The system enforces a multi-tier testing strategy ensuring data integrity, mathematical correctness of optimization algorithms, and end-to-end API reliability:

```
┌─────────────────────────────────────────────────────────────┐
│                 End-to-End API Integration                  │
│       FastAPI TestClient • Route Handlers • DB Sessions      │
├─────────────────────────────────────────────────────────────┤
│                 Optimization & Math Tests                   │
│     Google OR-Tools CP-SAT Solver • Budget Ledger Math      │
├─────────────────────────────────────────────────────────────┤
│                 Core NLP & Parser Unit Tests                │
│    Regex Sluglines • 1/8ths Page Fractions • Dialogue Cues   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Test Suite Structure

Test files are located in `backend/tests/`:

| Test Module | Scope & Verification |
| :--- | :--- |
| [`test_script_parser.py`](file:///backend/tests/test_script_parser.py) | Screenplay regex patterns, slugline classification (INT/EXT, DAY/NIGHT), character cues, action lines, and 1/8th page math. |
| [`test_scheduler_service.py`](file:///backend/tests/test_scheduler_service.py) | Google OR-Tools CP-SAT model validity, daily 12-hour constraint adherence, location grouping, and company move minimization. |
| [`test_budget_service.py`](file:///backend/tests/test_budget_service.py) | Chart of accounts aggregation (ATL/BTL), 10% contingency compounding, 8% tax calculation, and ledger balance. |
| [`test_api_endpoints.py`](file:///backend/tests/test_api_endpoints.py) | Full HTTP life-cycle tests (`/api/health`, `/api/projects`, `/api/projects/demo/load`, `/api/schedule/generate`, `/api/budget/generate`). |

---

## 3. Running the Test Suite

### 3.1 Running All Tests
Navigate to the `backend` folder and run `pytest`:
```bash
cd backend
python -m pytest tests/ -v
```

### 3.2 Running Specific Test Suites
```bash
# Run Script Parser tests
python -m pytest tests/test_script_parser.py -v

# Run OR-Tools Scheduler tests
python -m pytest tests/test_scheduler_service.py -v

# Run Budget Ledger tests
python -m pytest tests/test_budget_service.py -v

# Run Full API Integration tests
python -m pytest tests/test_api_endpoints.py -v
```

### 3.3 Running with Code Coverage
To generate a coverage report:
```bash
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=term-missing
```

---

## 4. Verification Results & Test Output

The complete backend test suite executes synchronously against a live in-memory/SQLite database, downloading and testing the real Hugging Face `dslim/bert-base-NER` pipeline and Google OR-Tools solver:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\lilly\OneDrive\Desktop\Movie\backend
configfile: pyproject.toml
collected 5 items

tests/test_api_endpoints.py::test_health_check PASSED                    [ 20%]
tests/test_api_endpoints.py::test_create_project_and_demo_seed PASSED   [ 40%]
tests/test_budget_service.py::test_budget_generation PASSED              [ 60%]
tests/test_scheduler_service.py::test_schedule_optimization PASSED      [ 80%]
tests/test_script_parser.py::test_script_parser_slugline_and_dialogue PASSED [100%]

======================== 5 passed in 317.45s (0:05:17) ========================
```
*Note: The initial run takes ~5 minutes because PyTorch loads and caches `dslim/bert-base-NER` (~430 MB) and builds the local wordpiece index. Subsequent runs execute in seconds.*

---

## 5. Automated Frontend Build Verification

The frontend React single-page application is verified using Vite's production bundling pipeline:

```bash
cd frontend
npm run build
```

### Build Verification Results:
- **Modules Processed**: 2,355 modules
- **Output Bundle**: Cleanly generated into `frontend/dist/`
- **Errors**: 0
- **Warnings**: 0

---

## 6. Continuous Integration (CI) Guidelines

For automated GitHub Actions or GitLab CI workflows, create `.github/workflows/ci.yml`:

```yaml
name: Continuous Integration

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          python -m spacy download en_core_web_sm
      - name: Run Pytest
        run: |
          cd backend
          python -m pytest tests/ -v

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install and Build
        run: |
          cd frontend
          npm install
          npm run build
```
