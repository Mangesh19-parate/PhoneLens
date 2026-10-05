# PhoneLens: Progress Tracker

## Gate 0: Decisions Before Code (All Complete)

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| G0-01 | Syllabus / mandated algorithms check | **Done** | Decision D-23 in `MEMORY.md`: Standard candidate suite applied. |
| G0-02 | Check target machine & environment | **Done** | Decision D-24 in `MEMORY.md`: Python 3.13.14 on Win11 verified; deps imported successfully. |
| G0-03 | Confirm dataset provenance, licence, currency | **Done** | Decision D-25 in `MEMORY.md` & `README.md`: SHA-256 `d0816ac...` computed, INR assumption and licensing caveats documented. |

## M0: Setup & Harness

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| M0-01 | Create repository skeleton & guidelines | **Done** | Full package directories created; `AGENTS.md` populated with non-negotiable rules. |
| M0-02 | Dependencies & Makefile | Pending | |
| M0-03 | Central config (`config.py`) | Pending | |
| M0-04 | Lint and test harness | Pending | |
| M0-05 | Place raw CSV and loader | Pending | |

## Milestone Tracker Summary

| Milestone | Description | Status | Total Tasks | Completed Tasks |
|---|---|---|---|---|
| Gate 0 | Decisions before code | **Done** | 3 | 3 |
| M0 | Setup (Skeleton, Deps, Config, Makefile, CI) | In Progress | 5 | 1 |
| M1 | Data (Clean, Groups, Split, Audit) | Pending | 7 | 0 |
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
