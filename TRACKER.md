# PhoneLens: Progress Tracker

## Gate 0: Decisions Before Code

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| G0-01 | Syllabus / mandated algorithms check | **Done** | Decision D-23 recorded in `MEMORY.md`: None required; standard suite applies. |
| G0-02 | Check target machine & environment | **Done** | Decision D-24 recorded in `MEMORY.md`: Python 3.13.14 on Win11 verified; all deps dry-run and imported successfully. |
| G0-03 | Confirm dataset provenance, licence, currency | Pending | |

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
