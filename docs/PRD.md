# PhoneLens: Product Requirements Document

| | |
|---|---|
| Version | 1.0 |
| Date | 2026-10-04 |
| Derived from | `spec.md` v1.3.2 (freeze candidate) |
| Status | Draft for implementation |
| Rule | If this document and `spec.md` disagree, `spec.md` wins. Change the spec first, then this file. |

---

## 1. Summary

PhoneLens is a small web application that takes a smartphone's specifications and returns three things: an estimated price in INR with an honest range, a Budget, Mid-range or Premium classification with probabilities, and a set of market views built from a 980-phone dataset. It is a college practical project built to the standard of a careful machine-learning engineer: the work that matters is leakage control, grouped validation and truthful uncertainty, not the number of features.

It is a reproducible, offline-trained decision application. It is not a production ML platform and it is not a live price tool.

## 2. Problem

Smartphone price models are easy to build and easy to get wrong. Three failures are specific to this dataset and each would be visible to an examiner within minutes:

1. **A classifier that cheats.** `price_segment` is just `price` cut at fixed thresholds. A model given `price` scores 100% and means nothing.
2. **Validation that leaks.** 424 of 980 rows belong to clusters of near-duplicate listings (RAM or storage variants, and the same phone under different names). Random folds put siblings on both sides of the split and inflate every score.
3. **Confidence that is not earned.** A single global error band covers cheap phones too generously and flagships too narrowly, and hides that behind a good-looking average.

The product has to avoid all three and show the evidence that it did.

## 3. Users

| Persona | Who | What they need |
|---|---|---|
| **Presenter** | The student building and defending the project | One-command reproducibility, numbers they can defend, a five-minute demo that works offline |
| **Examiner** | The person grading the practical | Visible evidence of rigour: audit, leakage guard, grouped validation, uncertainty, failure cases |
| **Curious buyer** | Someone holding a spec sheet and wanting a price sense | Plain language, a range instead of a false-precision number, similar phones to compare |

The Curious buyer drives the interface. The Examiner drives the Models page and the data notes. The Presenter drives the build process.

## 4. Goals and non-goals

### 4.1 Goals

1. Price prediction with a nominal 80% range, sensitivity and five comparable phones.
2. Classification into three segments with probability estimates, cross-checked against the price model.
3. Filterable analytics, including a Value Finder that ranks phones by distance from their spec-implied range.
4. A Flask application that loads pre-trained artifacts and never trains at request time.
5. A minimal, light interface built from the supplied design tokens.
6. Evidence of rigour that is visible inside the product, not only in a report.

### 4.2 Non-goals

No deep learning, accounts, database, Docker or Kubernetes, MLflow, live scraping or mobile app. No XGBoost, LightGBM or SHAP. No claim of real market pricing. No HP branding or marks.

## 5. Success measures

The product is successful when every Must requirement below is implemented, every quality gate in section 8 passes (or fails openly and is reported as such), and the five-minute demo in `spec.md` §14.2 runs on the target machine with the network off.

| Measure | Target | Where checked |
|---|---|---|
| Must requirements implemented | 100% | `TRACKER.md` traceability matrix |
| Quality gates | All pass or are reported as failed | `TRACKER.md` gate table |
| Demo | Completes in five minutes, offline | M9-05, M9-03 |
| Test suite | `make ci` green, 80% or more coverage on `src/` | QG-11, QG-13 |

## 6. Functional requirements

### 6.1 Predict

| ID | Requirement | Statement | Acceptance | Spec | Priority |
|---|---|---|---|---|---|
| FR-P1 | Spec input form | A form with the 23 model inputs in five fieldsets (Basics, Performance, Display, Battery and charging, Cameras), using the controls in spec §3.2. It is prefilled with the Mid-range preset, and Budget, Mid-range and Flagship presets come from real dataset rows. | One click on Estimate price returns a result with no edits. Presets load without a page reload. | §3.2, §9.2, §10.3 | Must |
| FR-P2 | Price estimate and nominal range | Return a price in INR and a nominal 80% range, plus the observed held-out coverage for the request's price band and its n. | The range brackets the point estimate. The caption shows coverage and n from metrics.json. The UI never says "80% confidence". | §6.4 | Must |
| FR-P3 | Sensitivity | For the top 8 numeric features, show how the estimate changes when the feature is set to the dataset median, using the single non-causal template. | Template test passes; no output contains "adds", "costs" or "worth". | §6.5 | Should |
| FR-P4 | Comparable phones | Show five nearest phones (RAM, storage, battery, refresh rate, rear MP, cores, CPU tier) with name, price and the specs that differ. | Distances equal scikit-learn brute-force distances; ties break by row index. | §6.5 | Should |
| FR-P5 | Notices | Show a notice when any input is outside the training range, and when a brand or processor brand is rare or unseen and is treated as Other. | An unseen brand returns 200 with a warning and category_status, never 422. | §9.4 | Must |
| FR-P6 | Validation feedback | Show per-field errors from 422 responses inline. Fast charging is a three-state choice, and expandable-storage capacity appears only when the toggle is on. | The three fast-charging states round-trip; cross-field violations name the offending field. | §9.3, §9.4 | Must |
| FR-P7 | Model provenance | Show the model name, version and training date with each result. | The model object in the response is rendered on the result card. | §9.3 | Should |

### 6.2 Classify

| ID | Requirement | Statement | Acceptance | Spec | Priority |
|---|---|---|---|---|---|
| FR-C1 | Segment prediction | Predict Budget, Mid-range or Premium and give probability estimates for all three classes. | Probabilities sum to 1; the classifier never receives price. | §8 | Must |
| FR-C2 | Calibration honesty | A caption states whether calibration was applied. Probabilities are described as calibrated only if the calibrated variant was selected. | Caption text follows the calibration decision recorded in manifest.json. | §8.3 | Must |
| FR-C3 | Borderline check | Compare the classifier's segment with the segment implied by the regressor's estimate. Show a Borderline badge if they disagree or the 80% range straddles 20,000 or 40,000. | Unit tests cover agreement, disagreement and straddling cases. | §8.5 | Must |
| FR-C4 | Cross-link and comparables | The result shows the comparables table and a link, See the price estimate for these specs, that carries every input in the query string. | Following the link opens Predict with the same values filled in. | §8.6, §10.3 | Should |

### 6.3 Analytics

| ID | Requirement | Statement | Acceptance | Spec | Priority |
|---|---|---|---|---|---|
| FR-A1 | Global filters | Filters for segment (multi-select), brand (top 12 plus Other), price range (log slider) and 5G (any, yes, no). Filter state lives in the query string. | Reloading or sharing the URL reproduces the view. | §7.1 | Must |
| FR-A2 | Views | Thirteen views: kpi, price_dist, segment_mix, brand_price, ram_price, storage_price, refresh_price, fiveg, charging, battery_scatter, corr, value, data_notes. | Each view returns chart-ready data, a one-line takeaway and its caveat. | §7.2 | Must |
| FR-A3 | Small-group suppression | Any group with n below 10 is hidden or greyed and labelled "n < 10". | Brand rankings show 17 brands, not 46. | §7.1 | Must |
| FR-A4 | Table alternative | Every chart has a details element holding a data table with the same numbers. | Table values equal the chart payload. | §10.3, §10.6 | Must |
| FR-A5 | Value Finder | Rank phones by absolute score, label them above or below the spec-implied range, show the fixed diagnostic banner, and exclude prices above 150,000 unless the toggle is on. | abs(score) above 1 exactly when the listed price is outside the interval; the words bargain and overpriced never appear. | §7.3 | Must |
| FR-A6 | Data notes | An accordion that presents the §2.2 audit, the §2.3 caveats and the group-audit counts. | All twelve audit issues appear with their handling. | §2.2, §2.3, §3.1 | Must |

### 6.4 Models page

| ID | Requirement | Statement | Acceptance | Spec | Priority |
|---|---|---|---|---|---|
| FR-M1 | Metrics | Show cross-validation mean ± sd and test point estimates for both modules. Show bootstrap CIs if the artifact exists, otherwise label them "CIs omitted". | The page renders correctly with and without the bootstrap artifact. | §5, §10.3 | Must |
| FR-M2 | Diagnostics | Confusion matrix, reliability diagram and permutation importance by feature group. Partial dependence is optional. | Figures come from artifacts, not from recomputation at request time. | §6.5, §8.3 | Should |
| FR-M3 | Failure modes and transparency | List the §6.6 failure examples, coverage per segment with n, the brand-held-out figure, the calibration decision and the group-audit counts. | Every item in model_card.md section list is present on the page. | §6.6, §12.4 | Must |

### 6.5 Platform

| ID | Requirement | Statement | Acceptance | Spec | Priority |
|---|---|---|---|---|---|
| FR-S1 | Home page | Three module cards and four headline facts from the kpi view, with the audit headline. | Facts match the kpi payload. | §9.2 | Should |
| FR-S2 | Offline operation | Fonts, Plotly and all scripts and styles are served from static/. No page makes an external request. | The demo works with the network disabled. | §9.5 | Must |
| FR-S3 | Version guard | The app refuses to start when scikit-learn, numpy, pandas or joblib differ in exact version from the manifest, or Python differs in major.minor. An override flag turns the failure into a banner. | Guard tests cover mismatch, match and override. | §9.1 | Must |
| FR-S4 | Service endpoints | /healthz, /api/meta/options and /api/models/metrics exist; every API error uses one JSON shape. | Contract tests pass for all status codes in spec §9.3. | §9.2, §9.3 | Must |
| FR-S5 | Snapshot labelling | The UI and model card state that the data is a static snapshot of listing prices, that currency is assumed INR, and that the app is not a live price tool. The footer carries the design-reference line. | Text is present on Home, Predict and Models pages and in the footer. | §1.2, §2.3, §10.1 | Must |

Priority key: **Must** is required for acceptance. **Should** is expected but appears on or near the cut list in `spec.md` §13.1. **Could** is optional.

## 7. Non-functional requirements

| ID | Area | Requirement | Acceptance | Spec |
|---|---|---|---|---|
| NFR-1 | Performance: Latency | POST /api/predict p95 under 150 ms on a laptop, with sensitivity variants scored in one batched call. | tests/test_latency.py passes. | §9.5 |
| NFR-2 | Reproducibility: Deterministic training | Same seed gives metrics equal within rtol 1e-6 and atol 1e-8; dataset hash, feature list, config, split indices and manifest are identical. | tests/test_reproducibility.py passes. | §11, §12.3 |
| NFR-3 | Accessibility: WCAG 2.2 AA | Visible labels, aria-live on results, aria-describedby on errors, full keyboard use, contrast at or above AA, data tables for charts. | The manual checklist passes; no colour-only signal. | §10.6 |
| NFR-4 | Responsive: 375 px to 1440 px | Layouts adapt at the five breakpoints in §10.6. Touch targets are at least 44 by 44 px. No horizontal page scroll. | Checked at 375, 768 and 1440 px. | §10.6 |
| NFR-5 | Security: Hygiene | CSP and related headers, no cookies or sessions, a 16 KB body limit, Jinja autoescape on, debug off in Production. | Header and 413 tests pass. | §9.5 |
| NFR-6 | Quality: Lint, tests, coverage | make ci runs ruff and pytest; coverage on src/ is at least 80%. | make ci exits 0 and the coverage report shows 80% or more. | §11 |
| NFR-7 | Honesty: Statistical honesty | Quality gates are never loosened to pass; leakage audit triggers are followed; wording rules (nominal range, non-causal sensitivity, diagnostic Value Finder) hold everywhere. | Gate thresholds in config match the spec; copy tests pass. | §5, §6, §8, §10.7 |
| NFR-8 | Portability: Runs on a lab machine | Works on Windows without make (documented equivalents), with Python 3.12 or a supported version, offline. | README lists every command with a non-make equivalent; verified on the target machine. | §12.1, §15 |
| NFR-9 | Maintainability: Single sources of truth | One feature list, one config module, and a webapp that imports only service/predictor.py. | Import-graph test passes. | §3.2, §4 |

## 8. Quality gates

Gates are acceptance tests for the models and the system. They are never loosened to make a run pass. If a gate fails, the failure procedure in `docs/IMPLEMENTATION_PLAN.md` applies and the report says so.

| ID | Gate | Threshold | Spec | Recorded by |
|---|---|---|---|---|
| QG-01 | Regression beats tuned Ridge on the primary metric | MdAPE lower in at least 10 of 15 paired folds and mean paired gain above 0.005 | §6.3 | M3-07 |
| QG-02 | Regression sanity floors on the locked test set | MdAPE at most 16%; R² at least 0.82 | §6.3 | M5-04 |
| QG-03 | Regression upper limit | Test R² above 0.93 triggers the full leakage audit; run not accepted until it passes | §6.3 | M5-04 |
| QG-04 | Interval coverage | Overall 0.72 to 0.88; every segment at least 0.65; report n per segment | §6.4 | M5-04 |
| QG-05 | Classification floors and baseline | Test macro-F1 at least 0.80 and above regress-then-bin by more than 0.01, or the report says it did not | §8.4 | M4-06 |
| QG-06 | Classification upper limit | Accuracy of 0.97 or more triggers the full leakage audit | §8.4 | M5-04 |
| QG-07 | Leakage audit passes | Feature-list test; no group on both sides; shuffled-label R² at most 0.05 and accuracy at most majority rate plus 0.05; top-feature ablation reported | §5 | M3-06 |
| QG-08 | Calibration decision recorded | Lower mean log loss over CV_SPLITS wins; a difference under 0.005 goes to uncalibrated | §8.3 | M4-03 |
| QG-09 | Group audit | 733 groups; 424 rows in multi-row groups; zero under-merged clusters; row_id runs 0 to 979 | §3.1 | M1-03 |
| QG-10 | API latency | POST /api/predict p95 under 150 ms | §9.5 | M7-07 |
| QG-11 | Coverage | At least 80% on src/ | §11 | M9-04 |
| QG-12 | Reproducibility | Same seed, metrics within rtol 1e-6 and atol 1e-8; hashes identical | §11 | M9-04 |
| QG-13 | CI | make ci exits 0 | §1.3 | M9-04 |
| QG-14 | Manual UI checklist | Keyboard-only, 375 px, reduced motion, offline load all pass | §10.6, §11 | M9-05 |

A score above an upper limit is a trigger for scrutiny, not proof of leakage.

## 9. User stories

| ID | As a | I want to | So that | Requirements |
|---|---|---|---|---|
| US-01 | Curious buyer | pick the Mid-range preset and click Estimate price | I get a price and a range without filling in 23 fields | FR-P1, FR-P2 |
| US-02 | Curious buyer | change RAM and see how the estimate moves | I understand what the model is responding to, without being told RAM causes a price | FR-P3 |
| US-03 | Curious buyer | see five similar phones with their real prices | I can sanity-check the estimate without trusting the model | FR-P4 |
| US-04 | Curious buyer | be told when my inputs are outside what the model has seen | I know when to distrust the estimate | FR-P5, FR-P6 |
| US-05 | Curious buyer | classify the same specs as Budget, Mid-range or Premium with probabilities | I see how close the phone is to a boundary | FR-C1, FR-C2, FR-C3 |
| US-06 | Curious buyer | jump from a segment result to the price estimate for the same specs | I do not retype anything | FR-C4 |
| US-07 | Curious buyer | filter the market views by segment, brand, price and 5G, and share the URL | someone else sees what I see | FR-A1, FR-A2, FR-A3 |
| US-08 | Curious buyer | see which phones are listed above or below what their specs imply | I find interesting cases, understanding it is a ranking and not a verdict | FR-A5 |
| US-09 | Examiner | read the data audit and the duplicate-group counts inside the app | I can check that leakage and duplicates were handled | FR-A6, FR-M3 |
| US-10 | Examiner | see cross-validation and test metrics, interval coverage per segment, calibration decision and failure cases | I can judge whether the numbers are honest | FR-M1, FR-M2, FR-M3 |
| US-11 | Presenter | run the whole app offline on a Windows lab machine | the demo does not depend on the network or on make | FR-S2, NFR-8 |
| US-12 | Presenter | retrain and get the same numbers | I can defend every figure in the viva | NFR-2, NFR-7 |

## 10. Content rules that are requirements

These come from the honesty requirement (NFR-7) and apply to every screen, API field and document:

| Rule | Detail |
|---|---|
| Interval wording | "Nominal 80% range", never "80% confidence". Observed coverage is shown beside it. |
| Sensitivity wording | One template: "Setting RAM to the dataset median (6 GB) instead of your 8 GB changes this model's estimate by −₹2,100." Never "adds", "costs" or "is worth". |
| Value Finder wording | "Listed above spec-implied range" and "Listed below spec-implied range". Never "bargain" or "overpriced". The diagnostic banner is always visible. |
| Calibration wording | State whether calibration was applied. Do not call probabilities calibrated unless the calibrated variant was selected. |
| Snapshot wording | Static snapshot, listing prices, assumed INR, not a live price tool. |
| Product wording | Plain and specific. No "AI-powered", no exclamation marks. |

## 11. Assumptions, dependencies and constraints

| # | Item | Status |
|---|---|---|
| A-1 | Prices are INR | Supported circumstantially, not confirmed (`spec.md` §2.1) |
| A-2 | Python 3.12 is available on the target machine | To confirm in G0-02 |
| A-3 | The syllabus does not require algorithms beyond those listed | To confirm in G0-01 |
| A-4 | Dataset licence permits academic use with attribution | Not confirmed; G0-03 |
| A-5 | Modern evergreen browsers (current Chrome, Edge, Firefox, Safari) | Assumption of this document, not stated in the spec |
| C-1 | scikit-learn, pandas, numpy, Flask, pydantic, joblib at the versions in `spec.md` §12.2 | Fixed |
| C-2 | No internet at demo time | Fixed |
| C-3 | One developer, deadline unknown | Planning constraint; the cut list handles it |

## 12. Risks

The full register with owners lives in `TRACKER.md`. The ones that decide whether the project lands:

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Implementation surface area exceeds the deadline | High | High | Follow the cut list (spec §13.1) in order; never cut the items on the never-cut list |
| R-02 | The practical's syllabus requires algorithms the spec does not list | Medium | High | Gate 0 before M0; add them as rows in the candidate tables under the same protocol |
| R-03 | Dataset source, licence or currency stays unconfirmed | Medium | Medium | G0-03; keep the INR caveat and say the licence is not confirmed until checked |
| R-04 | Lab machine Python or library versions differ | Medium | High | Check in G0-02; requirements.lock; retrain with make train on the demo machine |
| R-05 | No make on Windows | High | Low | Document equivalent python -m commands in the README |
| R-06 | Final tuned metrics miss a gate | Medium | High | Do not loosen thresholds; apply the failure procedure in the implementation plan and report honestly |
| R-07 | Premium interval coverage is noisy (about 42 test rows) | High | Low | Gate is 0.65 per segment; always report n |
| R-08 | Pickled models break across machines | Medium | High | Exact-version guard; plain dict bundles of sklearn and numpy objects, no custom classes |
| R-09 | Plotly cartesian bundle filename or version not available | Medium | Low | Fall back to the full minified bundle at 3.2.0 |
| R-10 | The ₹ glyph is missing from the vendored Manrope build | Low | Low | Arial fallback supplies it; check during M8-01 |
| R-11 | An agent edits thresholds, the feature list or tests to make a gate pass | Medium | High | AGENTS.md hard rules; spec-first change control; gate constants live only in config.py |
| R-12 | Playwright cannot be installed on the lab machine | Medium | Low | Manual checklist is the documented fallback |
| R-13 | Antigravity rule-file limit or folder names differ from the sources used here | Low | Low | AGENTS.md is kept under 12,000 characters; verify rules loading in the installed version |

## 13. Open items

1. **Syllabus-required algorithms** (G0-01). Settle before any code.
2. **Dataset source, licence and currency** (G0-03). Must close before submission.
3. **Target machine versions** (G0-02). Settle early; it decides whether the lock file is enough.

## 14. Release criteria

A release candidate exists when all of the following are true:

1. Every Must requirement in section 6 and section 7 is implemented and traceable to a passing test or a recorded manual check.
2. Every gate in section 8 is recorded in `TRACKER.md` with the measured value.
3. `make ci` exits 0 and coverage on `src/` is at least 80%.
4. The manual UI checklist (QG-14) is recorded.
5. Every number in the report equals the corresponding value in `artifacts/metrics.json`.
6. The README states the INR assumption, the licence status and the attribution.

## 15. Related documents

| Document | Purpose |
|---|---|
| `spec.md` | Source of truth |
| `docs/TRD.md` | How it is built |
| `docs/APP_FLOW.md` | How users and data move through it |
| `docs/UI_UX_DESIGN.md` | How it looks and behaves |
| `docs/BACKEND_SCHEMA.md` | Every data and API shape |
| `docs/IMPLEMENTATION_PLAN.md` | Ordered tasks |
| `docs/PROJECT_STRUCTURE.md` | Where everything lives |
| `TRACKER.md` | Status and evidence |
| `MEMORY.md` | Decisions and traps |
| `AGENTS.md` | Rules for coding agents |