# PhoneLens: Progress Tracker

## Gate 0: Decisions Before Code (All Complete)

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| G0-01 | Syllabus / mandated algorithms check | **Done** | Decision D-23 in `MEMORY.md`: Standard candidate suite applied. |
| G0-02 | Check target machine & environment | **Done** | Decision D-24 in `MEMORY.md`: Python 3.13.14 on Win11 verified; deps imported successfully. |
| G0-03 | Confirm dataset provenance, licence, currency | **Done** | Decision D-25 in `MEMORY.md` & `README.md`: SHA-256 `d0816ac...` computed, INR assumption and licensing caveats documented. |

## M0: Setup & Harness (All Complete)

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| M0-01 | Create repository skeleton & guidelines | **Done** | Full package directories created; `AGENTS.md` populated with non-negotiable rules. |
| M0-02 | Dependencies & Makefile | **Done** | `requirements.txt`, `requirements-dev.txt`, and `Makefile` created; targets mapped to non-make equivalents in `README.md`. |
| M0-03 | Central config (`config.py`) | **Done** | `src/phonelens/config.py` created with all paths, seeds, thresholds, and quality gate constants. |
| M0-04 | Lint and test harness | **Done** | `pyproject.toml` configured; `test_smoke_import.py` and `test_import_graph.py` created; `pytest` and `ruff check .` clean. |
| M0-05 | Place raw CSV and loader | **Done** | `data/raw/smartphone_v5.csv` placed; `load.py` implemented with `file_sha256()` and `load_raw()`; unit tests passing. |

## M1: Data (Clean, Groups, Split, Audit)

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| M1-01 | Loader with explicit schema and row_id | **Done** | `schema.py` defines 41 `RAW_COLUMNS` & `validate_raw()`; `load_raw()` attaches contiguous `row_id` (0..979); tested in `tests/test_clean.py`. |
| M1-02 | Cleaning pipeline | **Done** | `data/clean.py` implemented (idempotent, sentinels 143/68, invariants asserted, `model_display` kept); `phones_clean.csv` generated. |
| M1-03 | Duplicate grouping and collision audit | Pending | |
| M1-04 | Outer split | Pending | |
| M1-05 | CV_SPLITS, brand-holdout splitter and positions_for | Pending | |
| M1-06 | Data tests | Pending | |
| M1-07 | EDA notebook / clean data script | Pending | |

## Milestone Tracker Summary

| Milestone | Description | Status | Total Tasks | Completed Tasks |
|---|---|---|---|---|
| Gate 0 | Decisions before code | **Done** | 3 | 3 |
| M0 | Setup (Skeleton, Deps, Config, Makefile, CI) | **Done** | 5 | 5 |
| M1 | Data (Clean, Groups, Split, Audit) | In Progress | 7 | 2 |
| M2 | Feature & Preprocessing Contract | Pending | 3 | 0 |
| M3 | Regression Pipeline | Pending | 7 | 0 |
| M4 | Classification Pipeline | Pending | 6 | 0 |
| M5 | Intervals, Explanations, OOF, Contract Freeze | Pending | 8 | 0 |
| M6 | Analytics Logic | Pending | 5 | 0 |
| M7 | Flask API | Pending | 7 | 0 |
| M8 | UI (Pages, Components, Charts) | Pending | 10 | 0 |
| M9 | Audit & Verification | Pending | 6 | 0 |

## Quality Gates Status

| ID | Gate | Target Threshold | Measured Value | Status |
|---|---|---|---|---|
| QG-01 | Regression beats Ridge | MdAPE wins in >= 10 of 15 folds, mean gain > 0.005 | — | Pending |
| QG-02 | Regression sanity floor | Test MdAPE <= 16%, Test R² >= 0.82 | — | Pending |
| QG-03 | Regression upper limit | Test R² > 0.93 triggers full audit | — | Pending |
| QG-04 | Interval coverage | Overall [0.72, 0.88], each segment >= 0.65 | — | Pending |
| QG-05 | Classification baseline | Test macro-F1 >= 0.80 and beats regress-then-bin by > 0.01 | — | Pending |
| QG-06 | Classification upper limit | Test accuracy >= 0.97 triggers full audit | — | Pending |
| QG-07 | Leakage audit | Zero overlap; shuffled R² <= 0.05, accuracy <= majority + 0.05 | — | Pending |
| QG-08 | Calibration decision | Mean log-loss comparison recorded; diff < 0.005 goes uncalibrated | — | Pending |
| QG-09 | Group audit | 733 groups, 424 multi-row rows, 0 under-merged clusters | — | Pending |
| QG-10 | API latency | POST /api/predict p95 < 150 ms | — | Pending |
| QG-11 | Test coverage | >= 80% coverage on `src/` | — | Pending |
| QG-12 | Reproducibility | Same seed produces metrics within rtol 1e-6, identical hashes | — | Pending |
| QG-13 | CI | `make ci` (or python equivalent) exits 0 | — | Pending |
| QG-14 | Manual UI checklist | Keyboard-only, 375px responsive, offline demo verified | — | Pending |
