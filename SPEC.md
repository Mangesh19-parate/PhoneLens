# PhoneLens: Project Specification

Smartphone price prediction, market analytics and segment classification, served through Flask.

| | |
|---|---|
| Version | 1.3.3 (freeze candidate: v1.0 plus three correction passes and three fixes found while deriving the documents; see §16) |
| Stack | Python 3.12, Flask 3.1, scikit-learn 1.8, pandas 3.0, vanilla JS, Plotly.js |
| Dataset | `smartphone_v5.csv`, 980 rows × 41 columns |
| Design source | `DESIGN-hp.md` (tokens adopted, HP branding not adopted; see §10) |
| Audience | The person implementing this, human or coding agent |

Tags used below: **[verified]** means measured on the uploaded CSV in the environment where this spec was written (Python 3.12.3, scikit-learn 1.8.0, pandas 3.0.2, numpy 2.4.4). **[assumed]** means it could not be checked and you should confirm it.

---

## 0. Decisions that override the original brief

The brief asked for three modules and a polished look. Building it the obvious way would produce a project that looks good and is wrong in ways an examiner can find in five minutes. These ten decisions prevent that. Each one is backed by a measurement, not a preference.

| # | Decision | Evidence |
|---|---|---|
| 1 | The classifier never sees `price`. | `price_segment` is a threshold on `price`: Budget below ₹20,000, Mid-range ₹20,000 to ₹39,999, Premium ₹40,000 and above. The cut-offs are inferred, and the lowest observed Premium price is ₹40,480 (§2.1). A model given `price` scored 100% accuracy **[verified]**. Without it: about 86%. The 100% result is a bug, not a model. |
| 2 | Cross-validation groups rows by duplicate cluster (`dup_group`), not by row. | 424 of 980 rows sit in clusters of near-duplicate listings: RAM/storage variants of one phone, and the same phone listed under different names (for example "iQOO 11 5G" and "iQOO 11 (16GB RAM + 256GB)", which have identical specs). Random K-fold puts siblings in both train and test. For the same model, R² is 0.873 with random folds, 0.861 grouped by base model name and 0.849 grouped by duplicate cluster; median error is 11.8%, 13.3% and 13.5% **[verified]**. |
| 3 | Models train on raw specs only. | Adding the engineered `performance_score` and `display_score` moved R² from 0.857 to 0.861, well inside fold noise (sd ≈ 0.04, repeated random CV) **[verified]**. The input form also cannot ask a user for a score they do not know. |
| 4 | `rating` is not a predictor. | It is a post-launch signal, unavailable when someone is pricing a phone. Including it adds about 0.006 R² **[verified]**. |
| 5 | scikit-learn only. No XGBoost, LightGBM, SHAP or PyTorch. | Random forest and histogram gradient boosting land within 0.01 R² of each other on 980 rows. The extra libraries add install risk on a college lab machine and no accuracy. Explainability is done with permutation importance, partial dependence and sensitivity deltas. |
| 6 | Design tokens yes, HP identity no. | The design file is HP's brand system. Its wordmark, chevrons and dark slabs are brand artifacts and conflict with the "minimal, light" requirement. Details in §10. |
| 7 | Report the honest number. | Headline metrics come from grouped CV and a locked test set, with a brand-holdout figure alongside (R² about 0.76). Do not report the best-looking split. |
| 8 | Preprocessing is dense and explicit. | `OneHotEncoder(sparse_output=False, handle_unknown="infrequent_if_exist", min_frequency=5)` inside `ColumnTransformer(sparse_threshold=0)`. Histogram gradient boosting accepted the default pipeline only because `ColumnTransformer` auto-densifies it; forcing sparse output makes it raise **[verified]**. With `handle_unknown="ignore"` an unseen brand encodes as all zeros instead of landing in the rare-brand bucket **[verified]**. |
| 9 | Intervals are set per predicted-price band and described as empirical coverage. | Over five outer folds a single global residual quantile covered 0.82 overall, but 0.89 of Budget and only 0.70 of Premium phones; per-band quantiles covered 0.82 overall, 0.82 of Budget and 0.78 of Premium **[verified]**. No finite-sample guarantee is claimed (§6.4). |
| 10 | Calibration is a tested choice, not a default. | On the prototype test fold an uncalibrated random forest had log loss 0.352; sigmoid calibration made it 0.364 (plain folds) or 0.365 (grouped folds) **[verified]**. The calibrated wrapper is adopted only if it wins on grouped CV (§8.3), and the UI says whether calibration was applied. |

---

## 1. Goals, non-goals, and what "senior-grade" means here

### 1.1 Goals

1. **Price prediction.** Given a phone's specs, return an estimated price in INR with an 80% interval, the main sensitivities, and five comparable phones from the dataset.
2. **Analytics.** Filterable views of the market structure in the dataset, plus a "Value Finder" that ranks phones by how far their listed price sits from what their specs predict.
3. **Classification.** Given the same specs, predict Budget, Mid-range or Premium with probability estimates, and cross-check the answer against the price model. Calibration is evaluated and reported, and the app claims calibrated probabilities only if the selected model is calibrated (§8.3).
4. **A Flask app** that loads pre-trained artifacts and never trains at request time.
5. **A clean, minimal, light UI** built from the supplied design tokens.

### 1.2 Non-goals

No deep learning, no user accounts, no database, no Docker or Kubernetes, no MLflow, no live scraping, no mobile app. The dataset is a static snapshot, so the app must never present itself as a live market price tool. PhoneLens is a reproducible, offline-trained ML decision application. It is not a production ML platform, and the report should not call it one.

### 1.3 Senior-grade checklist

Polish alone does not read as senior work. These do, and each one has an acceptance test in §13.

1. A written data audit with real findings, shown in the app.
2. A leakage guard: a test that fails if `price`, `price_segment` or `rating` enters the feature list.
3. Grouped, stratified, seeded validation, with a locked test set that is never used for selection or tuning.
4. Baselines for every model (dummy, linear, and "regress then bin" for the classifier).
5. Uncertainty on every prediction, with measured coverage.
6. Failure modes documented with real examples from the data.
7. Reproducible artifacts with a manifest (data hash, library versions, seed).
8. Tests, linting and one command (`make ci`) that runs both.

---

## 2. Dataset audit

### 2.1 Profile

| Item | Finding |
|---|---|
| Shape | 980 rows, 41 columns, no nulls, no duplicate rows, 980 unique `model` strings **[verified]** |
| Currency | INR, supported circumstantially and not confirmed: brands such as iQOO, Poco, Tecno, Infinix and Lyf; a median of 19,994.5; and a related Kaggle dataset listing (1,020 raw rows) that says it was scraped from SmartPrix, an Indian price-comparison site. The relation to v5 is unconfirmed. Confirm against the original dataset's metadata before submission. Until then the UI says "INR" and the model card states the assumption. |
| Price | Min 3,499, median 19,994.5, mean 32,520, max 650,000. Heavily right-skewed. Only 13 rows above 150,000 **[verified]**. |
| Segments | Budget 506 (51.6%), Mid-range 263 (26.8%), Premium 211 (21.5%) **[verified]**. Cut-offs used everywhere: Budget `price < 20,000`, Mid-range `20,000 ≤ price < 40,000`, Premium `price ≥ 40,000`, held as constants in `config.py`. They are inferred: the data show Budget max 19,999, Mid-range max 39,999 and Premium min 40,480, so any cut-off in (39,999, 40,480] fits, and 40,000 is the natural round value. The observed minimum Premium price (₹40,480) is a data fact, not the threshold. |
| Brands | 46 brands. Only 17 have 10 or more phones. Top: xiaomi 134, samsung 132, vivo 111, realme 97, oppo 88 **[verified]**. |
| OS | android 923, ios 46, other 11 **[verified]** |
| Provenance | 980-row smartphone datasets circulate under several names: a Kaggle "Smartphone Dataset" (22 columns), and a "Real World Smartphones Dataset" (980 phones with brand, price, rating, processor, camera, OS and display fields) listed on Gigasheet. v5's row count and most base columns resemble these, so v5 is probably an extended version of one of them. I could not confirm which one, who the original author is, or the licence. The extra 19 columns are engineered and undocumented. Before submitting: identify the original source, cite it, check its licence, and state that the score columns have unknown provenance. |

### 2.2 Issues found and how each is handled

| # | Issue | Evidence | Handling |
|---|---|---|---|
| 1 | Target leakage in `price_segment` | See §0 decision 1 | Excluded from features. Used only as the classification target. |
| 2 | Near-duplicate listings | 424 rows sit in multi-row clusters: 348 share a base name, and 76 more are the same phone under a different name (spec-identical) | `dup_group` via union-find over name and spec fingerprint (§3.1); all splits and CV are grouped on it. |
| 3 | Sentinel values in `fast_charging` | −1 for 143 rows (equal to `fast_charging_available == False`); 0 for 68 rows where charging is available but wattage is unknown | Convert to `fast_charging_w`: NaN when the value is ≤ 0. Keep `fast_charging_available`. |
| 4 | Garbage in `battery_score` | Exactly `battery_capacity × fast_charging`, so it is negative for 143 rows and 0 for 68 | Dropped. |
| 5 | Redundant exact transforms | `memory_power = ram × storage`, `camera_score = rear_mp × num_rear_cameras`, `total_camera_mp = rear_mp + front_mp`, all with 100% match | Dropped. They double-count raw features and distort importance. |
| 6 | Mislabeled `resolution_type` | "Ultra HD" is assigned to 589 rows with 1080-pixel width | Dropped. |
| 7 | Truncated `screen_size` | Integer inches; 931 of 980 rows equal 6 | Dropped (no signal). Also drops `screen_category`. |
| 8 | Truncated `processor_speed` | Integer GHz, values 1, 2, 3 | Kept, labelled "CPU speed tier". |
| 9 | Inconsistent processor strings | 311 rows contain double spaces; 214 unique names collapse to 149 after cleanup | Normalise whitespace and case. |
| 10 | Extreme luxury outliers | Vertu Signature Touch at 650,000; Redmi K20 Pro Signature Edition at 480,000; Mate 50 RS Porsche Design at 239,999 | Kept in the data, log-transform the target, report robust metrics, list as known failure cases. |
| 11 | Binned copies of raw columns | `ram_category`, `storage_category`, `battery_type` | Dropped. |
| 12 | Engineered columns with unknown provenance | `performance_score`, `display_score`, `battery_density` | Excluded from models. `display_score` and `performance_score` may appear in analytics labelled "as published in dataset". |

### 2.3 Caveats to state in the app and the report

Listing prices are not sales prices. Brand mix reflects who is in the dataset, not market share. Some phones are years old and were priced at launch. Correlation in the analytics module is not causation.

---

## 3. Cleaning and feature policy

### 3.1 Cleaning steps (in `src/phonelens/data/clean.py`)

Run in this order. The function is pure and idempotent: running it twice gives identical output.

1. Load with an explicit column list. Fail fast if any expected column is missing. Assign `row_id = np.arange(len(df))` at ingestion, the row's position in the raw CSV. `row_id` is never reset, reordered or re-derived: every group, split, `CV_SPLITS` entry, out-of-fold prediction and analytics record refers to rows by `row_id`, never by a pandas positional index or a label that survived a `reset_index`.
2. Normalise strings in `brand_name`, `processor_brand`, `processor_name`, `os`: lowercase, strip, collapse internal whitespace. Keep the original `model` as `model_display`.
3. Create the grouping keys. `base_model`: lowercase `model`, remove any parenthesised text such as `(8GB RAM + 128GB)`, collapse whitespace. `spec_fingerprint`: the joined values of `brand_name`, normalised `processor_name`, `battery_capacity`, `fast_charging`, `refresh_rate`, `resolution_width`, `resolution_height`, `num_rear_cameras`, `primary_rear_camera_mp`, `primary_front_camera_mp`, `has_5g`, `has_nfc`, `has_ir_blaster`, `os`, `num_cores` and `processor_speed`; it deliberately excludes RAM, storage and expandable storage. `dup_group`: union-find (disjoint-set union with path compression, root = lowest `row_id`) that unites any two rows sharing a `base_model` or a `spec_fingerprint`. `dup_group` is the grouping key for every split, CV fold and calibration fold.
4. Create `fast_charging_w` (NaN where `fast_charging <= 0`). Log the counts of −1 and 0 rows.
5. Assert invariants: `price > 0`; segment matches the 20,000/40,000 thresholds; `extended_upto == 0` whenever `extended_memory` is false; `ram_capacity` between 1 and 18.
6. Write `data/processed/phones_clean.csv`. Use CSV, not parquet, to avoid a `pyarrow` dependency. Under pandas 3 string columns default to the `str` dtype and copy-on-write applies, so write code without chained assignment.

**Collision audit.** `clean.py` writes the counts below to `reports/group_audit.json`, the Models page shows them, and a test checks them. Measured on the shipped CSV **[verified]**:

- Base-name grouping alone gives 785 groups and 348 rows in multi-row groups. Union-find over name and fingerprint gives 733 groups and 424 rows in multi-row groups (largest group: 6 rows).
- *Over-merging* (distinct devices forced into one group): of 153 multi-row base-name groups, 3 contain members that differ in a non-memory spec, for example an "Infinix Note 12 (G96)" variant with a different processor. Over-merging makes validation slightly harsher and cannot cause leakage, so it is accepted.
- *Under-merging* (one phone left in separate groups): 47 spec-identical clusters (128 rows) spanned more than one base name, such as "Motorola Moto G62 5G" and "Motorola Moto G62 (8GB RAM + 128GB)". Under-merging does cause leakage, and it is what the fingerprint union fixes. After the union the count of such clusters is zero by construction, and the test asserts it.
- Remaining limit: different phones from one brand with identical specs (for example two ROG Phone variants) are merged. That is the conservative direction again.

### 3.2 Model features (23 columns)

| Feature | Type | Form control |
|---|---|---|
| `brand_name` | categorical | Dropdown of the brands the fitted encoder keeps (5+ training phones), plus "Other" (see §5, rare and unseen categories) |
| `processor_brand` | categorical | Dropdown |
| `os` | categorical | Dropdown (android, ios, other) |
| `has_5g`, `has_nfc`, `has_ir_blaster` | binary | Toggles |
| `num_cores` | numeric | Dropdown (4, 6, 8) |
| `processor_speed` | numeric (tier 1–3) | Segmented control, labelled "CPU speed tier" |
| `ram_capacity` | numeric (GB) | Dropdown of values seen in training |
| `internal_memory` | numeric (GB) | Dropdown of values seen in training |
| `extended_memory`, `extended_upto` | binary, numeric | Toggle; capacity dropdown appears only when on |
| `battery_capacity` | numeric (mAh) | Number input with training min/max |
| `fast_charging_available`, `fast_charging_w` | binary, numeric (NaN allowed) | Three-way choice: none / yes with wattage / yes, wattage unknown |
| `refresh_rate` | numeric (Hz) | Dropdown (60, 90, 120, 144, 165, 240) |
| `resolution_width`, `resolution_height`, `pixel_per_inches` | numeric | A resolution preset fills all three; an "Advanced" disclosure allows editing |
| `num_rear_cameras`, `num_front_cameras` | numeric | Steppers |
| `primary_rear_camera_mp`, `primary_front_camera_mp` | numeric | Number inputs |

The same feature list is used by the regressor and the classifier. It lives in one place, `features/spec.py`, so the two cannot drift apart.

### 3.3 Columns never used as features

| Column | Reason |
|---|---|
| `price`, `price_segment` | Targets |
| `rating` | Post-launch signal |
| `model` | Identifier. Used for grouping and display only. |
| `battery_score`, `memory_power`, `camera_score`, `total_camera_mp` | Exact arithmetic on raw columns |
| `performance_score`, `display_score`, `battery_density` | Engineered upstream, provenance unknown, no measurable gain |
| `screen_size`, `screen_category`, `resolution_type`, `ram_category`, `storage_category`, `battery_type` | Truncated, mislabeled or binned copies |
| `processor_name` | Used for analytics and display only in v1. A chipset-tier feature is an optional stretch goal, adopted only if it beats the raw feature set by more than one fold standard deviation. |

---

## 4. Architecture and repository layout

Training is offline. Flask only loads artifacts and serves them.

```
 OFFLINE                                              ONLINE (Flask)
 raw CSV ─► clean ─► split ─► train + tune ─► artifacts/ ──► predictor.py ─► /api/*
                        │           │              ▲                          │
                        └─► evaluate (test, once)  │                     pages + JS
                            build_analytics ───────┘
```

```
phonelens/
├── README.md
├── spec.md
├── Makefile                      # setup, data, train, evaluate, run, test, lint, ci
├── requirements.txt              # lower bounds
├── requirements-dev.txt          # pytest, ruff
├── requirements.lock             # pip freeze from the machine that trained the artifacts
├── data/
│   ├── raw/smartphone_v5.csv
│   └── processed/phones_clean.csv
├── src/phonelens/
│   ├── config.py                 # paths, seed, thresholds, feature groups
│   ├── data/    {load.py, clean.py, groups.py, schema.py, split.py}
│   ├── features/{spec.py, build.py}         # feature lists, build_preprocessor("tree" | "linear")
│   ├── models/  {regression.py, classification.py, uncertainty.py,
│   │             evaluate.py, explain.py, comparables.py}
│   ├── analytics/{aggregates.py, value_finder.py}
│   └── service/{predictor.py, artifacts.py}  # predictor is the only thing Flask imports;
│                                             # artifacts.py = save/load, manifest, version guard
├── scripts/  {train.py, evaluate.py, build_analytics.py}
├── artifacts/                    # committed for the demo; regenerated by `make train`
│   ├── regressor.joblib   classifier.joblib   comparables.joblib
│   ├── metrics.json       manifest.json       model_card.md
│   └── analytics.json     # OOF predictions and precomputed aggregates
├── webapp/
│   ├── __init__.py               # create_app()
│   ├── routes/ {pages.py, api.py}
│   ├── schemas.py                # pydantic request/response models
│   ├── templates/ {base.html, home.html, predict.html, classify.html,
│   │               analytics.html, models.html, partials/}
│   └── static/ {css/, js/, fonts/, vendor/}
├── tests/
└── notebooks/01_eda.ipynb        # exploration only; nothing imports from it
```

Rules: `webapp/` imports only `service/predictor.py`. `scripts/` are thin wrappers around `src/`. No module reads a global path directly; everything comes from `config.py`.

---

## 5. Shared ML protocol

| Item | Rule |
|---|---|
| Seed | 42, set once in `config.py` and passed everywhere. |
| Outer split | One fold of `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`, stratified on `price_segment`, grouped on `dup_group`: 784 training rows, 196 test rows, zero shared duplicate groups **[verified]**. |
| Test-set rule | The locked test set is never used for model selection, hyperparameter tuning, calibration choice, interval calibration, threshold selection, feature engineering or performance-sensitive explainability (importance and sensitivity use validation folds and training data). It is used for final performance reporting only: metrics, interval coverage, the confusion matrix and, when computed, bootstrap CIs. Descriptive features that fit nothing, namely Comparables and Analytics, may use the full static dataset, but they never influence training or evaluation. Training functions receive training frames only, and `scripts/evaluate.py` is the only place that reads test rows. |
| Inner CV | Three deterministic split sets on the training portion, `StratifiedGroupKFold(5, shuffle=True, random_state=s)` for `s` in (11, 22, 33), concatenated into one list of 15 (train, validation) pairs of `row_id` arrays called `CV_SPLITS`. Every tuning, comparison and calibration-selection step consumes this same list. scikit-learn needs positional indices, so exactly one helper, `positions_for(frame, row_ids)`, converts `row_id` arrays into positions for the frame being fitted; nothing else converts, and a test checks that the round trip returns the same `row_id`s. |
| Tuning | One `RandomizedSearchCV(cv=CV_SPLITS, n_iter=25, random_state=42)` per candidate model. Each sampled configuration is scored on all 15 folds and selection is by mean score. scikit-learn accepts an explicit list of splits here **[verified]**. Regression tuning uses a custom scorer that implements the MdAPE definition in §6.1 (the target is `log1p(price)`, so the scorer inverts both prediction and truth with `expm1`). |
| Reporting | Mean ± sd across the 15 folds, plus the paired per-fold difference against a baseline (win count and mean gain). The folds overlap, so the sd understates the real uncertainty, and the report says so. No standard-error rule is used. |
| Selection | Best mean CV score on the primary metric (MdAPE for regression, macro-F1 for classification). A pre-declared practical margin δ decides ties: δ = 0.005 for MdAPE (half a percentage point) and δ = 0.01 for macro-F1. A more complex model must beat a simpler one by more than δ on the mean, otherwise the simpler one wins. Complexity order: Ridge or logistic regression, then random forest, then histogram gradient boosting. |
| Preprocessing | Two builders in `features/build.py`: `build_preprocessor("tree")` and `build_preprocessor("linear")`. Both use the same categorical block, `OneHotEncoder(sparse_output=False, handle_unknown="infrequent_if_exist", min_frequency=5)`, inside `ColumnTransformer(..., sparse_threshold=0)`, so every output is dense. The tree numeric block is passthrough and leaves NaN in `fast_charging_w` (random forest and histogram gradient boosting handle NaN natively in scikit-learn 1.8). The linear numeric block is `SimpleImputer(strategy="median", add_indicator=True)` then `StandardScaler`. All of it lives inside a `Pipeline`; nothing is fit outside a fold. |
| Rare and unseen categories | The fitted encoder is the single source of truth. A category seen fewer than 5 times in the fitted data (`rare`) and a category never seen at all (`unseen`) land in the same "infrequent" column **[verified]**; a frequent category (`known`) gets its own column. The API reports the status per field (§9.4) and accepts all three, so an unseen brand is a 200 with a warning, not a 422. The UI's "Other" simply sends a value that is not in the dropdown list. The dropdown list is read from the fitted encoder (`categories_` minus `infrequent_categories_`), never recomputed from the full CSV. `os` has no infrequent bucket (android, ios and other each have 5+ rows) and is the only strict enum, so an unseen `os` is a 422 and cannot reach the encoder. No custom normaliser is needed. |
| Brand generalisation | Diagnostic on the training portion only. `GroupKFold(n_splits=5)` (deterministic, no shuffle), groups = `brand_name`, so each brand is wholly held out in exactly one fold and all 46 brands take part. Hyperparameters are fixed to the selected model's, with no per-fold re-tuning. Report pooled, sample-weighted R² (log) and MdAPE over all out-of-fold predictions, plus a per-brand MdAPE table for the 17 brands with n ≥ 10. Prototype result: R² 0.76, MdAPE 17.6% **[verified]**. |
| Leakage audit | Runs as tests on every training run. (1) Feature-list test: no `price`, `price_segment`, `rating`, `model` or score column. (2) Group test: no `dup_group` on both sides of any split. (3) Label-shuffle test: refit with the training labels randomly permuted; regression R² must be at most 0.05 and classification accuracy at most the majority rate plus 0.05 (prototype: R² −0.26, accuracy 0.443 against a majority rate of 0.517 **[verified]**). (4) Top-feature ablation: refit without the single most important feature and report the change. A score above the §6.3 or §8.4 upper limit triggers the full audit, and the run is not accepted until all four checks pass. A high score is a trigger for scrutiny, not proof of leakage. |
| Test-set CIs | Optional (first on the cut list, §13.1). When computed: 1,000 bootstrap resamples that resample whole `dup_group` groups, stored as an artifact. State plainly that n ≈ 196 makes the intervals wide. When the artifact is absent, the Models page shows test point estimates and labels the CIs "omitted". |
| Persistence | `joblib`, with a `manifest.json` (see §12). |

---

## 6. Module A: Price prediction

### 6.1 Target and metrics

Target: `log1p(price)`. Predictions are inverted with `expm1`.

| Metric | Role |
|---|---|
| Median absolute percentage error (MdAPE) | Primary. Robust to the luxury outliers. |
| R² on log price | Secondary |
| MAE in INR, on all rows and on "mainstream" rows (price ≤ 150,000) | Secondary. Raw MAE is dominated by a handful of flagships. |
| Error by segment (MAE and MdAPE per Budget, Mid-range, Premium) | Diagnostic. Shown in the model card. |

Definitions live in `models/evaluate.py`, one function each, and are unit-tested against hand-computed values. With `z_hat` the model output on the log scale and `price` the listed price in INR: `mdape = median(|expm1(z_hat) − price| / price)`, computed in INR after inversion and never on log residuals; R² is computed on `z = log1p(price)`; MAE is computed in INR. `evaluate.py` exports no function that could compute MdAPE on log residuals.

### 6.2 Candidates

| Model | Purpose | Tuned parameters |
|---|---|---|
| `DummyRegressor(strategy="median")` on log price | Floor | none |
| `Ridge` | Interpretable linear baseline | `alpha`, log-uniform 0.01–1000, tuned by the same `RandomizedSearchCV(cv=CV_SPLITS)` as every other model. `RidgeCV` is not used because it runs its own internal CV, which would break the shared-splits rule. |
| `RandomForestRegressor` | Candidate | `n_estimators` 300–800, `min_samples_leaf` 1–4, `max_features` 0.3–1.0 |
| `HistGradientBoostingRegressor` | Candidate | `learning_rate` 0.03–0.1, `max_iter` 200–600, `max_leaf_nodes` 8–31, `l2_regularization` 0–1 |
| Syllabus-required models (for example `DecisionTreeRegressor`, `KNeighborsRegressor`, `SVR`) | Added if your practical names them. They enter the same comparison and selection protocol. KNN and SVR use `build_preprocessor("linear")`; the decision tree uses the tree preprocessor. | One small grid each |

### 6.3 Expected results and gates

Prototype baselines **[verified]**: raw features, `StratifiedGroupKFold(5)` grouped on `dup_group`, all 980 rows.

| Model | R² (log) | MdAPE |
|---|---|---|
| Ridge | 0.815 | 16.3% |
| RandomForest | 0.864 | 13.4% |
| HistGradientBoosting | 0.848 | 13.4% |

The prototype Ridge row used `RidgeCV`; the protocol uses tuned `Ridge`, shown next.

Under the §5 splits (15 splits on the training portion) **[verified]**. Ridge `alpha` (about 11.5) was tuned on these splits; random forest and histogram gradient boosting use fixed prototype hyperparameters and are not yet tuned:

| Model | MdAPE, mean ± sd | R² (log), mean | Beats Ridge on MdAPE in | Mean paired MdAPE gain |
|---|---|---|---|---|
| Ridge (tuned) | 15.9% ± 1.6 | 0.808 | n/a | n/a |
| RandomForest | 14.3% ± 1.0 | 0.858 | 12 of 15 folds | 1.6 points |
| HistGradientBoosting | 14.9% ± 1.1 | 0.840 | 10 of 15 folds | 1.0 points |

Brand-held-out (§5 protocol, HistGradientBoosting): R² 0.762, MdAPE 17.6%.

Gates (checked by a test reading `metrics.json`):

- **One primary metric.** MdAPE drives tuning, selection and the acceptance gate. R² is reported as a secondary diagnostic and never overrides MdAPE.
- **Beat the baseline.** The selected model must have lower MdAPE than Ridge in at least 10 of the 15 paired folds, with a mean paired gain larger than δ = 0.005. In the table above both candidates pass: random forest comfortably (12 of 15 folds) and histogram gradient boosting narrowly (exactly 10 of 15). Random forest also leads histogram gradient boosting by about 0.6 points, which is more than δ, so it is the expected selection. If nothing passes, the report says so instead of claiming an improvement.
- **Sanity floors on the test set.** MdAPE at most 16% and R² at least 0.82.
- **Upper limit.** If test R² exceeds 0.93, the full leakage audit in §5 runs and the run is not accepted until it passes. A high score is a trigger for scrutiny, not proof of leakage.

The brand-held-out figure (R² ≈ 0.76) answers "how well does this do on a brand it has never seen". Report it in the model card next to the headline number.

### 6.4 Uncertainty

Method: residual-based prediction intervals with one quantile per predicted-price band, in the style of Mondrian conformal prediction. The spec calls the result an **empirical prediction interval**. It does not claim a formal coverage guarantee (see the last paragraph).

1. Compute grouped out-of-fold predictions `z_hat_oof` on the training portion with the selected model's fixed hyperparameters. Residuals are `r = |log1p(price) − z_hat_oof|`.
2. Assign each training row to a band by its predicted price `expm1(z_hat_oof)`: band A below 20,000, band B from 20,000 to 39,999, band C from 40,000. Bands use the segment thresholds and are known at inference time.
3. For each band take the `⌈(n_b + 1)·0.8⌉`-th smallest residual as `q_band`. If a band has fewer than 50 residuals, use the global quantile for it.
4. Refit the final model on all training data.
5. For a request, `z_hat` is the model output, the band comes from `expm1(z_hat)`, and the interval is `low = expm1(z_hat − q_band)`, `high = expm1(z_hat + q_band)`. This is the exact inverse of the `log1p` target. The multiplicative form `price·exp(±q)` differs from it by at most ₹0.35 on this data **[verified]**, so v1.0's formula gave essentially the same numbers; the change is for mathematical consistency.

Why per band. Over the five outer folds **[verified]**:

| Method | Overall | Budget | Mid-range | Premium |
|---|---|---|---|---|
| One global quantile | 0.82 ± 0.02 | 0.89 | 0.80 | 0.70 ± 0.06 |
| Per-band quantiles | 0.82 ± 0.03 | 0.82 | 0.84 | 0.78 ± 0.06 |

Typical quantiles across folds: about 0.23 for band A, 0.34 for band B and 0.43 for band C (global 0.31), which is a factor of roughly 1.26, 1.40 and 1.54 above and below the estimate, or full-interval ratios (`high / low`) of about 1.6, 2.0 and 2.4. A global quantile is too wide for cheap phones and too narrow for flagships, and it hides that behind a healthy-looking overall number.

Gates (read from `metrics.json`): test-set coverage overall between 0.72 and 0.88, and every segment at least 0.65. Premium has only about 42 test rows, so its binomial standard error at 0.80 is about 0.06 and single-fold Premium coverage is noisy (0.69–0.83 across the five outer folds); 0.65 sits roughly 2.5 standard errors below nominal. Report coverage per segment with n.

**What the UI says.** The interval is labelled "Nominal 80% range", never "80% confidence". Beneath it the result card shows the observed held-out coverage for the request's price band, for example "Observed on held-out phones in this band: 78% (n = 42)". The API returns the same numbers in `interval.observed_coverage`. A band's observed coverage can be below 80%, and the UI shows it as measured.

What is and is not claimed. The reported coverage is measured on this dataset. A formal finite-sample guarantee needs exchangeable data and a separate calibration set. Phone variants, grouped folds, and reusing out-of-fold residuals for a refitted model all break that, so the model card says "empirical coverage" and gives the numbers, nothing stronger.

### 6.5 Explainability (no SHAP)

- **Global importance.** Permutation importance computed on the validation part of each of the five folds in the first split set of `CV_SPLITS`, with the selected model refit on each fold's training part, 10 repeats, averaged across folds and aggregated by feature group (memory, battery, display, camera, processor, brand, connectivity). The test set is not used. Partial dependence plots for RAM, storage, battery and refresh rate use the final model and training-portion features only; they involve no labels.
- **Local sensitivity.** For a submitted phone, re-predict with each of the top 8 numeric features set to the training median, one at a time, and report the change in the model's estimate. The UI uses one template: "Setting RAM to the dataset median (6 GB) instead of your 8 GB changes this model's estimate by −₹2,100." It never says that a feature "adds", "costs" or "is worth" an amount, because trees are non-monotonic, features are correlated, and none of this is causal. A unit test checks the template output for those words.
- **Comparables.** Five nearest neighbours in standardised space over RAM, storage, battery, refresh rate, rear MP, cores and CPU tier. Implemented directly in numpy: a precomputed standardised matrix held in memory, squared Euclidean distances in one vectorised step, `np.partition` to find the 5th-smallest distance in O(N) rather than sorting all N, then every row at or below that distance (so all ties are kept), sorted by (distance, `row_id`) and cut to 5. Calling `np.argpartition` and sorting only its 5 picks is not enough: it chooses arbitrarily among ties at the cut-off, and on this dataset it disagreed with a full stable sort for 468 of 980 queries, because 551 queries have ties at the fifth neighbour **[verified]**. The threshold method matched the stable sort for all 980 and did not depend on row order **[verified]**. A test compares the distances with `sklearn.neighbors.NearestNeighbors(algorithm="brute")`; indices are not compared, because many phones have identical vectors and tie. At N = 980 a query takes about 0.07 ms **[verified]**, so no tree index is justified. The index is built from all 980 rows because it is a lookup over features, with no labels and no fitting involved. Show model name, price and the differing specs. This gives users a sanity check that does not rely on trusting the model.

### 6.6 Known failure modes (put these in the model card and the Models page)

Specs do not explain brand-driven or edition-driven pricing. From grouped out-of-fold predictions **[verified, approximate]**: Vertu Signature Touch is listed at 650,000 and predicted near 21,100; Redmi K20 Pro Signature Edition listed at 480,000 and predicted near 33,000; Huawei Mate 50 RS Porsche Design listed at 239,999 and predicted near 78,500; Apple iPhone 7s listed at 52,990 and predicted near 8,900. Old phones cause the opposite error: Google Pixel 4, Google Pixel 2 XL and OnePlus 6 come out overpredicted by roughly 2–3× their listed price. The UI shows an "extrapolation" notice when any input falls outside the training range.

---

## 7. Module B: Analytics

Analytics is descriptive. The only model-derived view is the Value Finder.

### 7.1 Global filters

Segment (multi-select), brand (top 12 plus "Other"), price range (slider on a log scale), 5G (any/yes/no). Filter state lives in the query string so a view can be shared and reloaded. All aggregation runs in pandas at request time on the cleaned frame (980 rows), memoised with `functools.lru_cache` on the normalised filter tuple.

**Suppression rule:** any group with n < 10 is hidden or greyed with the label "n < 10". This is why brand rankings show 17 brands, not 46.

### 7.2 Views

| ID | Title | Chart | What it computes | Caveat shown under the chart |
|---|---|---|---|---|
| `kpi` | Overview | Stat cards | Phone count, brand count, median price, % 5G, median RAM, % with fast charging | Snapshot data |
| `price_dist` | Price distribution | Histogram, log x-axis, segment bands | Counts per price bin, with the 20k and 40k boundaries | Long right tail |
| `segment_mix` | Segment mix by brand | 100% stacked bar | Share of Budget/Mid/Premium per brand (n ≥ 10) | Brand mix is not market share |
| `brand_price` | Brand price ranking | Horizontal bars with IQR whiskers | Median and IQR of price per brand (n ≥ 10) | Includes luxury outliers in IQR |
| `ram_price` | RAM vs price | Box plot | Price by RAM tier, log y-axis | Storage and RAM are correlated |
| `storage_price` | Storage vs price | Box plot | Price by storage tier | Same |
| `refresh_price` | Refresh rate vs price | Box plot | Price by refresh rate | 144 Hz and above have few rows |
| `fiveg` | 5G adoption | Grouped bars | % 5G per segment, median price with and without 5G | Confounded with chipset generation |
| `charging` | Charging by segment | Violin or box | Fast-charging wattage by segment (available and known only) | 211 rows have unknown or no wattage |
| `battery_scatter` | Battery vs price | Scatter, colour by segment | Battery capacity against log price | — |
| `corr` | Correlation | Heatmap | Spearman correlation across raw numeric features and log price | Collinear features; not causal |
| `value` | Value Finder | Sortable table plus scatter of listed vs predicted | Score = out-of-fold residual ÷ band quantile, per phone | See §7.3 |
| `data_notes` | Data notes | Accordion | The audit from §2.2 | — |

### 7.3 Value Finder

Uses grouped out-of-fold predictions over all 980 rows (`StratifiedGroupKFold(5)`, grouped on `dup_group`), computed once in `scripts/build_analytics.py` and stored in `analytics.json`. The hyperparameters are frozen from the model selected on the training portion only. This is deliberately not nested cross-validation: the view is a diagnostic, and nested CV would multiply the cost for no change in what it can honestly claim. The page states one residual caveat: the hyperparameters were tuned on training rows, so out-of-fold residuals for those rows are marginally optimistic, while test rows are clean. The view carries a fixed banner: "Diagnostic estimates from cross-validated predictions, not a performance statistic. Model performance is reported only on the locked test set (Models page)."

- For each phone: `resid = log1p(price) − z_hat_oof`, the band comes from `expm1(z_hat_oof)`, and `score = resid / q_band` using the §6.4 quantiles.
- `|score| > 1` means the listed price lies outside the model's 80% interval for that phone. **By construction about 20% of phones will.** The view is therefore a ranking sorted by `|score|`, never a verdict.
- Labels: "Listed above spec-implied range" for `score > 1`, "Listed below spec-implied range" for `score < −1`, and no label otherwise. Never use "bargain" or "overpriced". A phone above its range may be paying for a camera system, brand or software that the spec sheet does not capture.
- The default view excludes phones with price above 150,000, with a toggle to include them.

---

## 8. Module C: Classification

### 8.1 Task

**Framing.** `price_segment` is not an independently observed category. It is `price` cut at 20,000 and 40,000, so this task asks which price bin a phone's specs point to, and the regressor already answers that by binning its estimate (the regress-then-bin baseline). The classifier earns its place only through what the regressor cannot give: probabilities near the boundaries, for example Budget 0.42, Mid-range 0.55, Premium 0.03. The first paragraph of the classification section in the report says this. In the prototype it beat regress-then-bin (accuracy 0.866 against 0.845), and the gate in §8.4 must confirm that on the final run or the report says it did not.

Predict `price_segment` from the 23 model features. `price`, `rating` and every score column are excluded (§0, §3). Classes are ordered: Budget < Mid-range < Premium.

### 8.2 Models and baselines

| Model | Notes |
|---|---|
| Majority class | Accuracy 0.516 **[verified]** |
| Regress-then-bin | Use the price regressor, bin its output at 20,000 and 40,000. Required baseline: the classifier must justify existing. |
| `LogisticRegression` | Scaled, imputed; `C` tuned on `CV_SPLITS` like the others |
| `RandomForestClassifier` | `class_weight="balanced"` |
| `HistGradientBoostingClassifier` | Candidate |
| Syllabus-required models (for example `DecisionTreeClassifier`, `KNeighborsClassifier`, `SVC`, `GaussianNB`) | Added if your practical names them, under the same protocol. KNN, SVC and naive Bayes use `build_preprocessor("linear")`. |

Select on **macro-F1**, not accuracy, because Budget is 52% of the data.

### 8.3 Probability quality and calibration

Calibration is tested, not assumed. Two candidates for the final classifier: the chosen model as it is, and the chosen model inside `CalibratedClassifierCV(method="sigmoid", cv=CAL_SPLITS)`. Sigmoid is used because isotonic needs more data than the 211-row Premium class provides.

- `CAL_SPLITS` is an explicit list of (fit, calibrate) pairs, converted from `row_id` with the same helper, from `StratifiedGroupKFold(5, shuffle=True, random_state=5)`, grouped on `dup_group`, built from whatever training data the wrapper is being fitted on. Passing `cv=5` is forbidden: an integer uses plain stratified folds, which would place one variant of a phone in the fitted model and another in the calibration set, reintroducing the sibling leakage that §0 decision 2 removes. A test checks that the `cv` argument is a list and that no `dup_group` appears on both sides of any pair.
- Selection: evaluate both candidates on `CV_SPLITS`, rebuilding `CAL_SPLITS` inside each fold from that fold's training rows. Lower mean log loss wins; a difference under 0.005 goes to the uncalibrated model.
- Evidence from the prototype, one test fold **[verified]**: uncalibrated random forest log loss 0.352 and Brier 0.208; sigmoid with plain stratified `cv=5` 0.364 and 0.206; sigmoid with grouped splits 0.365 and 0.206. Grouping changed almost nothing (0.001 log loss). Neither calibrated variant beat the uncalibrated model on log loss, and Brier improved by only 0.002. Expect the uncalibrated model to be selected. That is a valid outcome, and the report states which was chosen and why.
- Report log loss, multiclass Brier score, and a reliability diagram for the chosen variant next to the alternative. The UI shows the probabilities of the selected variant with a caption stating whether calibration was applied ("Probability estimates. Calibration: not applied" or "Calibration: sigmoid, grouped"). It never describes probabilities as calibrated unless the calibrated variant was selected.

### 8.4 Expected results and gates

Prototype figures **[verified]** (`StratifiedGroupKFold(5)` on all 980 rows, grouped on `dup_group`; expect small differences under §5):

| Model | Accuracy | Macro-F1 |
|---|---|---|
| Majority class | 0.516 | — |
| Regress-then-bin (HistGradientBoosting) | 0.845 | 0.825 |
| Random forest | 0.866 | 0.848 |
| HistGradientBoosting | 0.839 | 0.817 |

Gates: test macro-F1 at least 0.80, and it must beat regress-then-bin by more than δ = 0.01 macro-F1, or the report states that it did not. An accuracy of 0.97 or higher triggers the full leakage audit in §5, and the run is not accepted until the audit passes; the audit is a trigger for scrutiny, not proof of leakage. Also report per-class precision and recall, the confusion matrix, quadratic weighted kappa, and the count of Budget↔Premium confusions. In the prototype only 5 of 980 predictions jumped across two classes; every other error was to an adjacent class. That is the right shape for an ordered target, and it belongs in the report.

### 8.5 Consistency check with Module A

For every submitted phone the API returns the classifier's segment and the segment implied by the regressor's point estimate. If they disagree, or the regressor's 80% interval straddles a boundary, show a "Borderline" badge. This is more useful to a user than a bare label.

### 8.6 Outputs

Predicted class, probability estimates for all three classes (with a line stating whether calibration was applied), the borderline flag, and the same comparables list as Module A.

---

## 9. Flask application

### 9.1 Structure and startup

- Application factory `create_app(config_name)` in `webapp/__init__.py`. Config classes: `Development`, `Production`, `Testing`. Debug mode is never on in `Production`.
- On startup, `service/predictor.py` loads the three joblib artifacts and `metrics.json` once and stores the `Predictor` on `app.extensions["predictor"]`. No model is loaded per request.
- **Version guard.** `manifest.json` records the versions used for training. At startup `artifacts.py` compares them with the running environment and refuses to start if scikit-learn, numpy, pandas or joblib differ in exact version, or if Python differs in major.minor. Python patch versions are not compared: pickle compatibility is stable across patches, and a lab machine's patch level is outside your control. The error message offers two fixes: `pip install -r requirements.lock`, or `make train` on this machine. Setting `PHONELENS_ALLOW_VERSION_MISMATCH=1` downgrades the failure to a banner on every page saying predictions may be unreliable, for an emergency demo only.
- Two blueprints: `pages` (HTML) and `api` (JSON, prefix `/api`). Request and response bodies are validated with pydantic v2 models in `schemas.py`.

### 9.2 Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Home: three module cards and four headline facts from `kpi` |
| GET | `/predict` | Price prediction page |
| GET | `/classify` | Segment classification page |
| GET | `/analytics` | Analytics page; `?view=<id>` plus filter params |
| GET | `/models` | Model card: metrics, calibration, importance, failure modes, data notes |
| GET | `/healthz` | Liveness plus artifact versions and training date |
| GET | `/api/meta/options` | Dropdown values (brand list read from the fitted encoder), numeric ranges, training medians (used only for sensitivity), and three real-row presets; the Mid-range preset is the form default |
| POST | `/api/predict` | Price estimate |
| POST | `/api/classify` | Segment |
| GET | `/api/analytics/<view_id>` | Chart-ready JSON for a view, honouring filters |
| GET | `/api/models/metrics` | Contents of `metrics.json` |

Presets (Budget, Mid-range, Flagship) are chosen by rule at build time (for example the row nearest each segment's median on the numeric features), not hard-coded phone names.

### 9.3 JSON contracts

`POST /api/predict` and `POST /api/classify` take the same body. Values below are illustrative.

```json
{
  "brand_name": "xiaomi",
  "processor_brand": "snapdragon",
  "os": "android",
  "has_5g": true,
  "has_nfc": false,
  "has_ir_blaster": true,
  "num_cores": 8,
  "processor_speed": 2,
  "ram_capacity": 8,
  "internal_memory": 128,
  "extended_memory": false,
  "extended_upto": 0,
  "battery_capacity": 5000,
  "fast_charging_available": true,
  "fast_charging_w": 67,
  "refresh_rate": 120,
  "resolution_width": 1080,
  "resolution_height": 2400,
  "pixel_per_inches": 395,
  "num_rear_cameras": 3,
  "num_front_cameras": 1,
  "primary_rear_camera_mp": 50,
  "primary_front_camera_mp": 16
}
```

Fast charging has three states and both fields are always sent (`null` is the wire value, since JSON has no NaN):

| State | `fast_charging_available` | `fast_charging_w` | Model input |
|---|---|---|---|
| No fast charging | `false` | `null` | NaN |
| Yes, wattage known | `true` | a number, 5–240 | the number |
| Yes, wattage unknown | `true` | `null` | NaN |

`/api/predict` response:

```json
{
  "currency": "INR",
  "price": 21400,
  "interval": { "nominal_level": 0.8, "method": "per_band_residual", "low": 15900, "high": 28700,
    "observed_coverage": { "band": "B", "coverage": 0.84, "n": 52, "overall": 0.82 } },
  "sensitivity": [
    { "feature": "ram_capacity", "label": "RAM", "submitted": 8, "median": 6, "delta_price": -2100,
      "text": "Setting RAM to the dataset median (6 GB) instead of your 8 GB changes this model's estimate by -₹2,100." }
  ],
  "comparables": [
    { "model": "Example Phone 5G", "price": 22999, "differs": ["ram_capacity", "refresh_rate"] }
  ],
  "category_status": { "brand_name": "known", "processor_brand": "known" },
  "warnings": ["battery_capacity is above the training range (max 22000)"],
  "model": { "name": "random_forest", "version": "2026-09-30", "trained_at": "2026-09-30T10:00:00Z" }
}
```

`/api/classify` response:

```json
{
  "segment": "Mid-range",
  "probabilities": { "Budget": 0.18, "Mid-range": 0.71, "Premium": 0.11 },
  "regressor_segment": "Mid-range",
  "borderline": false,
  "comparables": [ ],
  "category_status": { "brand_name": "known", "processor_brand": "known" },
  "warnings": [ ],
  "model": { "name": "random_forest", "calibration": "none", "version": "2026-09-30" }
}
```

Errors always use one shape:

```json
{ "error": { "code": "validation_error", "message": "Invalid input", "fields": { "ram_capacity": "must be between 1 and 24" } } }
```

Status codes: 200 success, 400 malformed JSON, 404 unknown API route (JSON, not HTML), 413 body over 16 KB, 422 validation failure, 500 generic message plus a request id.

### 9.4 Validation rules

Hard errors (422): wrong type; a value outside the allowed set for the one strict enum (`os`); a number outside physically plausible bounds (for example battery 1,000–25,000 mAh, RAM 1–24 GB, refresh rate 30–240 Hz); `extended_upto > 0` while `extended_memory` is false; `fast_charging_w` set while `fast_charging_available` is false.

Category fields. `brand_name` and `processor_brand` are constrained strings, not enums: trimmed, lowercased, 1–40 characters, and any such value is accepted. The response reports one status per field in `category_status`: `known` (frequent in the fitted encoder), `rare` (seen, but fewer than 5 times, so encoded in the infrequent bucket) or `unseen` (never seen, also encoded in the infrequent bucket). `rare` and `unseen` add a warning that the value is treated as "Other". An unseen brand is therefore a 200 with a warning, never a 422. Status comes from the fitted encoder's `categories_` and `infrequent_categories_`.

Soft warnings (200 with a `warnings` entry): value outside the training min–max, and unusual combinations such as `os = ios` with a non-Apple processor brand. A warning means "the model is extrapolating", and the UI shows it as a notice above the result.

### 9.5 Non-functional requirements

- `/api/predict` p95 under 150 ms on a laptop. Achieve it by scoring the sensitivity variants in a single batched `predict` call and keeping the comparables index in memory.
- Response headers: `Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:` (Plotly injects inline styles), `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`.
- No cookies and no sessions, so CSRF protection is not needed for the JSON API. Jinja autoescape stays on.
- All static assets (fonts, Plotly) are vendored under `static/`. The demo must work with no internet connection.
- One log line per request: method, path, status, duration, request id.

### 9.6 Complexity and data-structure choices

At 980 rows none of these is a performance necessity. The section records the reasoning so each choice can be defended.

| Operation | Choice | Cost | Why |
|---|---|---|---|
| Duplicate grouping | Union-find with path compression over two key dictionaries | O(N α(N)) | A transitive closure is needed (A shares a name with B, B shares specs with C), and naive pairwise comparison is O(N²) |
| Comparables | Vectorised distances, `np.partition` for the 5th-smallest distance, then a sort of only the rows at or below it | O(N·d) per query, d = 7, plus O(m log m) for the m rows at or below the cut-off | Selecting 5 of N needs no full O(N log N) sort; a tree index gives nothing at d = 7 and N = 980; measured about 0.07 ms per query |
| Sensitivity | One batched `predict` over 9 rows (the submitted spec plus 8 variants) | One model call instead of 9 | Per-call overhead dominates for tree models on single rows |
| Analytics filters | Cache key is a normalised, sorted tuple of the filter values | O(1) on a cache hit, O(N) on a miss (one pass over the filtered frame) | Equivalent filters in a different order must hit the same entry |
| Group aggregates | pandas `groupby`, then a count check | O(N) | Groups with n < 10 are suppressed at the aggregation step |
| Value Finder | Scores precomputed in `build_analytics.py`; sorted at request time only by the chosen column | O(N log N) per sort | Nothing is refitted or rescored per request |
| Startup | Artifacts loaded once into the app extension | One-off | No per-request deserialisation |

---

## 10. UI and design system

### 10.1 How `DESIGN-hp.md` is used

The file describes HP's commercial site. The requirement is "minimal, light". The two overlap on tokens and conflict on brand devices, so the rule is: keep the tokens and component shapes, drop the brand.

| Element in `DESIGN-hp.md` | Decision | Reason |
|---|---|---|
| White canvas, cloud and fog bands, ink text | **Adopt** | Core of the minimal light look |
| Electric Blue as the lone accent, at most two uses per viewport | **Adopt** for chrome and CTAs | Keeps the interface calm |
| 4px buttons and inputs, 16px cards, hairlines, Soft Lift shadow | **Adopt** | The sharp-controls, soft-containers split is the signature |
| Uppercase button labels with 0.7px tracking | **Adopt** | As specified |
| Pill category tabs, FAQ accordion, product-card layout | **Adapt** for filters, data notes and result cards | Reuse of shapes, new content |
| Forma DJR Micro typeface | **Replace** with Manrope | The file itself names Manrope as the closest open substitute, usable with no metric adjustment. Forma is proprietary. |
| Blue chevron decorations, HP wordmark, HP-specific photography | **Omit** | Trademarked brand artifacts; the design file says not to reuse the mark as generic decoration |
| Dark ink utility strip, help band and footer | **Omit** | Conflicts with "light". Footer is a cloud band with a hairline top border. |
| Bloom coral sale tags, storm teal accents | **Omit** | E-commerce and printer-plan specifics. `bloom-deep` is kept for error text only. |
| Blue used sparingly | **Exception for data-viz** | Chart series need distinguishable colours; see §10.5 |

Name and logo: the app is "PhoneLens" with a plain text wordmark set in Manrope 600. Do not use HP's name or marks anywhere. Add a footer line: "Visual style adapted from a public design-token reference; not affiliated with any brand."

### 10.2 Tokens

Define once in `static/css/tokens.css`. Everything else references variables.

```css
:root {
  /* colour */
  --color-primary: #024ad8;        --color-primary-bright: #296ef9;
  --color-primary-deep: #0e3191;   --color-primary-soft: #c9e0fc;
  --color-ink: #1a1a1a;            --color-charcoal: #3d3d3d;
  --color-graphite: #636363;       --color-steel: #c2c2c2;
  --color-canvas: #ffffff;         --color-cloud: #f7f7f7;
  --color-fog: #e8e8e8;            --color-error: #b3262b;
  --color-on-primary: #ffffff;

  /* shape */
  --radius-md: 4px;  --radius-lg: 8px;  --radius-xl: 16px;  --radius-pill: 9999px;

  /* spacing (8px base) */
  --space-xxs: 4px;  --space-xs: 8px;   --space-sm: 12px;  --space-md: 16px;
  --space-lg: 20px;  --space-xl: 24px;  --space-xxl: 32px; --space-section: 80px;

  /* elevation: soft lift on cards only; floating for transient overlays */
  --shadow-soft: 0 2px 8px rgba(26, 26, 26, 0.08);
  --shadow-float: 0 8px 24px rgba(26, 26, 26, 0.12);

  /* type */
  --font: "Manrope", Arial, sans-serif;
}
@media (max-width: 767px) { :root { --space-section: 48px; } }
```

Typography: self-host Manrope (variable woff2, SIL Open Font License) in `static/fonts/`. Weights 400, 500, 600, 700. Set display line-height to 1.0 and body line-height to 1.4 explicitly, as the design file advises for substitutes. All headings weight 500. Never below 12px.

| Use | Token | Size / weight |
|---|---|---|
| Home hero only | display-xl | 56 / 500 (36 on mobile) |
| Page title, primary result figure | display-lg | 44 / 500 (32 on mobile) |
| Section header | display-md | 32 / 500 |
| Card title | display-sm | 24 / 500 |
| Body | body-md | 16 / 400 |
| Lead text | body-lg | 18 / 400 |
| Captions, chart notes | caption-md | 14 / 400, colour graphite |
| Button | button-md | 14 / 600, uppercase, 0.7px tracking |

Format currency with `Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 })`. Check that the ₹ glyph renders in Manrope; if not, the Arial fallback supplies it.

### 10.3 Layout

Content max-width 1366px, 24px gutters, 80px between sections (48px on mobile). Top navigation is 64px tall on a white canvas with a hairline bottom border and a 2px blue underline on the active link: PhoneLens (left), Predict, Classify, Analytics, Models. Below 1024px the links collapse into a hamburger drawer. No utility strip.

Predict page:

```
┌ nav ───────────────────────────────────────────────────────────────┐
│ Estimate a phone's price                        (display-lg)       │
│ From specs, with a range and comparable phones. (body-lg, graphite)│
│ ┌ form card (16px radius, soft lift) ─────┐ ┌ result card, sticky ─┐│
│ │ Try an example: (Budget)(Mid)(Flagship) │ │ ₹21,400   (display-lg)││
│ │ ── Basics                               │ │ Nominal 80% ₹15,900 – ││
│ │ ── Performance                          │ │ ₹28,700   (graphite)  ││
│ │ ── Display                              │ │ Sensitivity (model)   ││
│ │ ── Battery and charging                 │ │ (sensitivity bars)    ││
│ │ ── Cameras                              │ │ Comparable phones     ││
│ │ [ ESTIMATE PRICE ]  (button-primary)    │ │ (5-row table)         ││
│ └─────────────────────────────────────────┘ └───────────────────────┘│
│ footer: cloud band, hairline top border                              │
└────────────────────────────────────────────────────────────────────┘
```

Form fields are grouped into `<fieldset>` sections, each with a `<legend>` in display-xs. The form is prefilled with the Mid-range preset, a real phone configuration from the dataset, so one click returns a result. Under the estimate the result card shows "Nominal 80% range" with a caption giving the observed held-out coverage for that price band and its n (§6.4). Medians are not used for prefilling: they cannot fill categorical fields and would produce a configuration no phone has. Below 1024px the result card moves under the form.

Classify page: the same form partial. The result card shows a segment badge, three horizontal probability bars (from the variant chosen in §8.3) and a caption stating whether calibration was applied, the borderline notice if triggered, and the same comparables table. A link "See the price estimate for these specs" carries the inputs across in the query string.

Analytics page: a pill tab row (category-tab) selects the view group; a filter bar (cloud band, 16px radius) sits above a two-column grid of chart cards (one column below 768px). Each chart card has a title, the chart, a one-line takeaway generated from the data, and the caveat from §7.2. The Value Finder card carries the §7.3 banner stating that its scores are diagnostics, not performance statistics. A `<details>` element under each chart holds a data table with the same numbers.

Models page: metrics table with mean ± sd and test point estimates (with bootstrap CIs when the artifact exists, otherwise labelled "CIs omitted"), confusion matrix heatmap, reliability diagram, permutation importance bars, failure-mode list, then the data notes as an accordion (faq-row pattern, 8px radius, hairline dividers).

### 10.4 Components

| Component | Spec |
|---|---|
| Primary button | Blue fill, white uppercase label, 44px tall, 12 × 24px padding, 4px radius. Pressed: `primary-deep`. Disabled: steel. One per view. |
| Secondary button | White fill, 1px ink border, ink label (`button-outline-ink`) |
| Text input, select | 44px, 4px radius, 1px graphite border (the design file uses steel, which is 1.8:1 on white and fails the 3:1 contrast WCAG 1.4.11 requires for control boundaries; deliberate accessibility deviation); focus gives a 1px ink border plus a 2px ink `:focus-visible` outline at 2px offset for keyboard users (deliberate accessibility addition) |
| Toggle and segmented control | Pill (`category-tab` shape); active state is ink fill with white text |
| Card | White, 16px radius, 24px padding, soft-lift shadow. Section bands stay flat. |
| Badge | `badge-pill-ink` for Premium, `badge-pill-outline` for Mid-range, soft-blue fill for Budget. Text always names the class; colour is never the only signal. |
| Table | Cloud header row, hairline row dividers, 14px text, numeric columns right-aligned, tabular numerals |
| Loading | Fog-coloured skeleton blocks, 150 ms fade; no spinners |
| Error and notice | Inline message under the field or above the result, `--color-error` text with a 1px border, never a browser `alert()` |

Motion: 150 ms opacity and transform only; disabled under `prefers-reduced-motion`.

### 10.5 Charts

Library: Plotly.js **3.2.0**, vendored (the CDN requires an exact version from v2 onward). Prefer the smaller `plotly-cartesian` partial bundle, which covers bar, box, scatter, histogram and heatmap; verify the file exists at that version when downloading and fall back to the full minified bundle if not.

- Font Manrope 12px, colour graphite. Transparent paper background, fog gridlines, no chart borders, no 3D, no pie or donut charts.
- Hover labels: ink background, white text. Modebar limited to "download PNG".
- Segment encoding (an ordered blue ramp built from the tokens): Budget `primary-soft` fill with a 1px `primary-deep` outline (the outline keeps the 3:1 graphical contrast), Mid-range `primary-bright`, Premium `primary-deep`.
- Neutral series use ink, graphite and steel. Highlights use `primary`.
- Correlation heatmap: diverging scale from `charcoal` (−1) through white (0) to `primary` (+1).
- Every chart has a text title, labelled axes with units, a legend or direct labels, and the caveat line beneath.
- Blue in charts is data encoding and does not count toward the "two blue elements per viewport" chrome rule.

### 10.6 Responsive behaviour and accessibility

Breakpoints from the design file: under 480, 480–767, 768–1023, 1024–1279, 1280 and up. Product-style grids go 4 → 3 → 2 → 1 columns. Every touch target is at least 44 × 44px.

Accessibility target is WCAG 2.2 AA: visible labels on every field, `aria-live="polite"` on result regions, `aria-describedby` for field errors, full keyboard operation, sufficient contrast (measured: white on `#024ad8` is 7.1:1, graphite on white is 6.0:1, error red on white is 6.5:1; `primary-bright` on white is 4.48:1, just under the 4.5:1 text threshold, so it is used for chart fills and never for text), and a data-table alternative for every chart.

### 10.7 Copy

Plain and specific. "Estimate price", not "Unlock insights". No "AI-powered", no exclamation marks. Every result carries its uncertainty, and every chart carries its caveat. Sensitivity text follows the single template in §6.5 and never uses causal wording ("adds", "costs", "is worth"). The interval is called "Nominal 80% range", never "80% confidence".

---

## 11. Testing and quality gates

Tests are written alongside each milestone (§13), not saved for the end.

| Area | Tests |
|---|---|
| Leakage | `test_no_leakage` (feature list), `test_group_overlap` (no `dup_group` on both sides of any split), `test_label_shuffle` (regression R² ≤ 0.05 and classification accuracy ≤ majority rate + 0.05 on shuffled labels). `test_leak_audit_triggers_when_price_is_a_feature`: training the classifier with `price` appended must exceed the §8.4 limit (≥ 0.97) and trigger the audit. |
| Cleaning | Idempotent; `row_id` is unique, runs 0 to 979 in raw-file order and survives `clean()` unchanged; sentinel counts equal 143 (−1) and 68 (0) on the shipped CSV; whitespace normalisation maps "Snapdragon  695" to "snapdragon 695"; `base_model("Realme 10 Pro (8GB RAM + 128GB)") == "realme 10 pro"`; `dup_group` places "iQOO 11 5G" and "iQOO 11 (16GB RAM + 256GB)" in one group; the collision audit reports zero under-merged fingerprint clusters. |
| Splitting and test-set discipline | No `dup_group` appears in both train and test; test segment proportions within 3 points of the full data; no test `row_id` appears in any list in `CV_SPLITS` (splits are stored and tested as `row_id` arrays, never positional indices); training functions accept training frames only. |
| Grouping | Union-find output is deterministic; the transitive case holds (rows A and B share a name, rows B and C share a fingerprint, so A, B and C land in one group). |
| Comparables | Top-5 distances from the numpy implementation equal those from `NearestNeighbors(algorithm="brute")` on 200 random queries; the result equals a full stable sort on (distance, `row_id`) and does not change when the rows are shuffled, including on queries with ties at the fifth neighbour. |
| Preprocessing | Output of both builders is dense; random forest and histogram gradient boosting fit on it; an unseen brand and a rare brand produce identical encoded rows; the brand dropdown equals the fitted encoder's `categories_` minus `infrequent_categories_`. |
| Metrics | `mdape` equals a hand-computed value on a small example; R² is computed on log price; no exported function computes MdAPE on log residuals. |
| Brand generalisation | Groups are `brand_name`; each brand appears in exactly one validation fold. |
| Calibration | The `cv` passed to `CalibratedClassifierCV` is a list of splits; no `dup_group` appears on both sides of any pair. |
| Uncertainty | Per-band `q` matches the finite-sample formula on a synthetic residual vector; a band with fewer than 50 residuals falls back to the global `q`; `low = expm1(z − q)` and `high = expm1(z + q)` are correct at prices of 3,499 and 650,000; `metrics.json` coverage meets the §6.4 gates. |
| Model gates | `metrics.json` satisfies the §6.3 and §8.4 gates, including the "too good" upper limits. |
| Predictor | A flagship spec predicts higher than an entry spec; probabilities sum to 1; the interval brackets the point estimate; an unseen brand maps to the rare bucket without error. |
| Explanations | The sensitivity text matches the §6.5 template and contains none of "adds", "costs", "worth". |
| API | 200 on valid input; 422 with per-field messages on a missing field, a bad `os` value and a cross-field violation; an unseen brand returns 200 with `category_status: unseen` and a warning; the three fast-charging states round-trip (`null` becomes NaN); 413 on an oversize body; 404 returns JSON for `/api/*`; `warnings` present when a value is out of range. |
| Analytics | Groups with n < 10 are suppressed; equivalent filters share a cache entry; Value Finder `score = resid / q_band` and `abs(score) > 1` exactly when the listed price is outside the interval. |
| Reproducibility | Training twice with the same seed gives the same results. Metrics are compared with `np.testing.assert_allclose(rtol=1e-6, atol=1e-8)`, because BLAS and threading can change the last digits; the dataset SHA-256, feature list, config, `CV_SPLITS` indices and manifest fields (except timestamps) are compared exactly. The version guard refuses to start on an exact-version mismatch for scikit-learn, numpy, pandas or joblib, or a Python major.minor mismatch, and the override flag shows the banner instead. |
| Style | `ruff check` and `ruff format --check` pass; type hints on every public function. |

Target coverage is 80% on `src/`, without chasing 100%. `make ci` runs lint plus tests. Three browser smoke tests run with `make smoke` (Playwright), outside `make ci` because Playwright downloads a browser binary that a lab machine may not allow: Predict preset gives a result and interval; Classify preset gives three probabilities and the calibration caption; changing an Analytics filter updates the chart data. If Playwright cannot be installed, the manual UI checklist in the README (keyboard-only pass, 375px width, reduced motion, offline load) is the fallback, and the report says so.

---

## 12. Reproducibility and documentation

### 12.1 Commands

| Target | Action |
|---|---|
| `make setup` | Create a virtualenv, install `requirements.txt` and `requirements-dev.txt` |
| `make data` | Clean the CSV and write the processed file |
| `make train` | Tune, select and fit both models; write artifacts and the manifest |
| `make evaluate` | Score the locked test set once; write `metrics.json` and figures |
| `make analytics` | Build out-of-fold predictions and aggregates |
| `make run` | `flask --app webapp run` |
| `make smoke` | Three Playwright browser smoke tests (optional; needs a browser binary) |
| `make ci` | Lint and test |

Many college machines run Windows without `make`. Provide the equivalent `python -m scripts.train` style commands in the README next to each target.

### 12.2 Dependencies

`requirements.txt` uses lower bounds from the environment this spec was verified in: `flask>=3.1.3,<3.2`, `scikit-learn>=1.8,<1.9`, `pandas>=3.0,<3.1`, `numpy>=2.0`, `joblib`, `pydantic>=2.7,<3`. Dev: `pytest`, `pytest-cov`, `ruff`. Optional: `waitress` for serving on Windows, `pytest-playwright` for `make smoke`. After training, run `pip freeze > requirements.lock` on the machine that produced the artifacts.

### 12.3 `manifest.json`

Fields: creation time (UTC), git commit if available, Python, scikit-learn, pandas, numpy and joblib versions, SHA-256 of the raw CSV, seed, feature list, split sizes, chosen model names and hyper-parameters, the `CV_SPLITS` seeds, the interval quantile for each price band, the calibration decision for the classifier, and a summary of headline metrics.

### 12.4 Model card (`artifacts/model_card.md`, shown on `/models`)

Intended use and non-use; data source, the §2.2 audit and the §3.1 group audit; features and exclusions with reasons; CV mean ± sd and test metrics for both modules (with bootstrap CIs when computed); per-segment errors; brand-held-out result; calibration; interval coverage; failure modes with the §6.6 examples; limitations (snapshot, INR assumption, listing prices); how to retrain.

### 12.5 README outline

What it is, one screenshot per module, five-command quickstart, results table, repository map, limitations, and attribution: the Kaggle dataset (check its licence), Manrope (SIL OFL), Plotly.js (MIT).

---

## 13. Build order and acceptance criteria

**Gate 0, before M0.** Get the practical's syllabus or marking rubric and settle §15 item 3. If it names algorithms, add them to the §6.2 and §8.2 candidate tables now; the comparison tables and the report depend on it.

The API and UI depend on a stable ML contract, and analytics depends on out-of-fold predictions, so the order is: data, shared preprocessing contract, models, intervals and OOF, analytics, API, UI. The contract is frozen at the end of M5; changing it after that means redoing M7 and M8.

Effort is a rough guess for one person: S is under half a day, M about a day, L two days or more. Treat these labels as lower bounds: `docs/IMPLEMENTATION_PLAN.md` breaks the work into 67 tasks and, assuming 1.5 hours for a small task, 4 for a medium and 8 for a large, totals about 24 working days against roughly 10.5 days if the labels below are summed. Both are guesses made without knowing your pace; if the deadline is under about three weeks, apply the §13.1 cut list from the start.

| Milestone | Effort | Done when |
|---|---|---|
| M0 Setup | S | Repo, dependencies, `config.py`, Makefile in place; `make ci` passes with placeholder tests |
| M1 Data | S | Clean CSV written; sentinel counts asserted; grouped stratified outer split tested; leakage test passing; group audit counts match §3.1 (733 groups, zero under-merged clusters) |
| M2 Feature and preprocessing contract | S | `features/spec.py` and both `build_preprocessor` variants done; rare and unseen category behaviour tested; `CV_SPLITS` and the brand-holdout splitter generated and saved |
| M3 Regression | L | Baselines and tuned model trained on `CV_SPLITS`; §6.3 gates pass; MdAPE scorer and definitions tested |
| M4 Classification | M | §8.4 gates pass; regress-then-bin comparison reported; calibration choice made on grouped CV and recorded |
| M5 Intervals, explanations, OOF, **contract freeze** | M | Per-band intervals meet §6.4 gates; permutation importance from validation folds; comparables index; OOF predictions written; `schemas.py` and the `/api/meta/options` shape frozen; artifacts and manifest final |
| M6 Analytics logic | M | Aggregates, suppression rule and Value Finder scores produced from `analytics.json` and the cleaned frame; tests green |
| M7 Flask API | M | All routes in §9.2 live; contract tests green; p95 under 150 ms; version guard works |
| M8 UI | L | Tokens and components implemented; Predict, Classify, Analytics and Models pages work end to end; keyboard-only pass done |
| M9 Audit | M | Model card, data-notes accordion and README complete; coverage target met; every §1.3 item verified; offline demo checked at 375px and 1440px; `make smoke` passes or the documented fallback is used |

Final acceptance is the §1.3 checklist: every item has a test or a visible artifact.

### 13.1 Cut list

Implementation surface area is the main risk for a college deadline, and a smaller system that fully meets the acceptance criteria beats a larger one that is partly mocked. If time runs short, cut in this order and keep everything else:

1. Bootstrap CIs on the test set (the Models page then shows point estimates labelled "CIs omitted", plus fold sd).
2. Partial dependence plots.
3. Violin and correlation-heatmap views.
4. The Value Finder scatter (keep the table).
5. Per-brand MdAPE table.
6. Comparables.
7. pydantic (replace with plain validation functions, same error shape).
8. Browser smoke tests (keep the manual checklist).

Never cut: the leakage guard, grouped splits, baselines, intervals with measured coverage, the API contract, the three module pages, the model card.

---

## 14. Submission pack

### 14.1 Report outline

1. Problem and scope. 2. Data and audit (the §2.2 table is the centrepiece). 3. Method (split, CV, models, uncertainty). 4. Results (baseline table, gates, brand-held-out figure, confusion matrix, calibration). 5. System (architecture diagram from §4, API contract). 6. Limitations and failure modes. 7. Conclusion and future work. 8. References and attribution.

### 14.2 Five-minute demo

1. Home page and the audit headline (30 s). 2. Predict with the Mid-range preset, show the interval and comparables (90 s). 3. Change RAM, show the sensitivity move (30 s). 4. Classify the same specs, show probabilities and the borderline badge (60 s). 5. Analytics: filter to Premium, open Value Finder, name one phone above its spec-implied price and explain why that is not the same as "overpriced" (60 s). 6. Models page: baselines, coverage, one failure case (30 s).

### 14.3 Likely viva questions

| Question | Answer grounded in this project |
|---|---|
| Why predict log price? | Price is right-skewed (median about 20k, max 650k) and errors are proportional; log makes the loss match how people judge price errors. |
| Why only about 86% classification accuracy? | Segments are bins of price. Phones near 20k or 40k are genuinely ambiguous. Feeding `price` gave 100%, which is why it is excluded. |
| Why grouped cross-validation? | 424 rows sit in clusters of near-duplicate listings. Random folds leak siblings and inflated R² from 0.849 to 0.873. |
| Why is grouping by model name not enough? | I audited it: 47 spec-identical clusters used different names ("iQOO 11 5G" against "iQOO 11 (16GB RAM + 256GB)"), so I merged rows with a union-find over name and spec fingerprint. Over-merging only makes validation harsher; under-merging leaks. |
| Why not XGBoost or a neural network? | On 980 rows the tree models tie within 0.01 R²; extra libraries add risk without gain. |
| What does the 80% interval mean, and how do you know it works? | It is a nominal 80% range from out-of-fold residuals, with one quantile per predicted-price band. Observed coverage across five held-out folds: 0.82 overall and 0.78 for Premium (about 42 phones per fold). It is empirical, not a formal guarantee, because grouped data and a refitted model break the exchangeability that guarantee needs. |
| Why drop the score columns? | They are exact arithmetic on other columns, or of unknown origin; adding them changed R² by 0.004, inside noise; and a user cannot enter them. |
| Where does it fail? | Luxury editions and old launch-priced phones, for example a 650,000 Vertu predicted near 21,100. |
| Is R² of about 0.85 good? | Better than Ridge (0.81); on unseen brands it falls to about 0.76, which shows brand premium is not in the specs. |
| What next? | Launch date, chipset benchmark scores, a separate luxury handling, monotonic constraints on RAM and storage. |
| Why keep a classifier if you can bin the regression? | The classifier gives probabilities near the 20k and 40k boundaries. In the prototype it also beat regress-then-bin (0.866 against 0.845 accuracy); the report states whether the final run confirmed that. |
| Did calibration help? | It was tested with group-aware folds. On the prototype test fold the uncalibrated forest had the best log loss (0.352 against 0.364–0.365), so the choice is made on grouped CV, the UI says whether calibration was applied, and the result is reported either way. |

---

## 15. Open items and assumptions to confirm

1. **Currency.** INR is supported circumstantially (§2.1) but not confirmed from the original dataset's metadata. Confirm before submission.
2. **Dataset source and licence.** Identify the original source (§2.1), cite it, and check its licence before submission. The licence is not confirmed.
3. **Syllabus requirements.** If your course requires named algorithms (for example KNN, SVM, Decision Tree), add them as extra rows in the candidate tables in §6.2 and §8.2. Keep the selection protocol unchanged; do not replace it. This is Gate 0 in §13: settle it before M0.
4. **Python version.** The environment used for verification runs Python 3.12. Confirm your lab machine has a version that current scikit-learn and pandas support; pip will refuse to install otherwise.
5. **Versions.** Flask 3.1.3 (released 18 February 2026), scikit-learn 1.8 and Plotly.js 3.2.0 were confirmed from release pages. The pydantic bound and the Plotly cartesian bundle filename were not confirmed; check them on install.
6. **Glyph check.** Confirm ₹ renders in the vendored Manrope build.
7. **Unverified provenance.** The upstream source of the engineered score columns is unknown. The spec avoids depending on them, but the report should say so plainly.
8. **Deliberate non-adoptions.** Nested CV for the Value Finder, a custom brand-normalising function and an exact Python patch-version match were considered and rejected; §16 says why.

---

## 16. Decision log

### 16.1 v1.0 to v1.1

A review of v1.0 raised fifteen points. Each was checked against the data or the library before the spec changed.

| Point | Outcome |
|---|---|
| One-hot output with histogram gradient boosting | **Adopted, but smaller than claimed.** It worked in v1.0 runs because `ColumnTransformer` auto-densifies; forcing sparse output makes it raise. Fixed with dense output and `sparse_threshold=0` (§5). |
| Calibration ignores groups | **Adopted.** The measured leakage effect was small (0.001–0.005 log loss, depending on the grouping scheme). The larger finding was that calibration did not beat the uncalibrated model, so it is now a tested choice (§8.3). |
| `log1p` interval inversion | **Adopted for consistency.** The old formula was off by at most ₹0.35. Fixed (§6.4). |
| Coverage claim | **Found during verification, not in the review.** v1.0 described an out-of-fold method but quoted coverage from a different one. The method as written covered Premium at 0.64–0.70 (depending on the grouping scheme), so intervals are now per band (§6.4). |
| "Test set touched once" versus permutation importance | **Adopted.** The rule is now "never used for selection or tuning", and importance moved to validation folds (§5, §6.5). |
| Value Finder optimism | **Adopted with the simpler option.** Hyperparameters frozen from the training portion, caveat stated. Nested CV rejected as disproportionate for a diagnostic (§7.3). |
| Prefill with "training medians" | **Adopted.** The form prefills with the Mid-range preset (§10.3). |
| "Other" brand handling | **Adopted with a simpler fix.** `handle_unknown="infrequent_if_exist"` gives the intended behaviour natively; a custom normaliser would add code without adding correctness (§5). |
| Classification is a binned regression target | **Adopted.** Framing added to §8.1 and the report outline. |
| Repeated CV definition | **Adopted.** One explicit list of 15 splits (§5). |
| Brand-held-out definition | **Adopted.** Exact protocol in §5. Re-measured under the v1.2 grouping: R² 0.76, MdAPE 17.6%. |
| Version guard strength | **Partly adopted.** Exact match for scikit-learn, numpy, pandas and joblib; Python compared at major.minor only, with an override banner (§9.1). |
| Over-engineering | **Partly adopted.** `registry.py` removed and a cut list added (§13.1); the architecture otherwise stands. |
| Causal wording in sensitivity | **Adopted.** Single template and a test (§6.5, §11). |
| MdAPE definition and build order | **Adopted.** One tested definition (§6.1); build order resequenced with a contract freeze (§13). |

### 16.2 v1.1 to v1.2

A second review raised fourteen points. Each was checked again; the grouping check produced a finding that changed several measured numbers.

| Point | Outcome |
|---|---|
| "Calibrated probabilities" versus an uncalibrated final model | **Adopted, honest option.** The goal now promises probability estimates; the UI states whether calibration was applied (§1.1, §8.3). |
| "Other" brand versus 422 validation | **Adopted.** `brand_name` and `processor_brand` are constrained strings with three statuses (`known`, `rare`, `unseen`); only `os` is a strict enum (§9.4). |
| Selection by MdAPE, gate by R² | **Adopted.** MdAPE is the single primary metric for tuning, selection and the gate; R² is secondary. Gate: lower MdAPE than Ridge in at least 10 of 15 paired folds with mean gain above δ. Measured: random forest 12 of 15; histogram gradient boosting 9 of 15 against the prototype RidgeCV and 10 of 15 against tuned Ridge (§6.3, §16.3). |
| `1e-9` reproducibility tolerance | **Adopted.** `rtol=1e-6, atol=1e-8` for metrics; exact comparison for hashes, config, split indices and manifest (§11). |
| `base_model` could merge different phones | **Adopted, with a finding in the opposite direction.** Over-merging is negligible (3 of 153 groups) and conservative. Under-merging is real: 47 spec-identical clusters (128 rows) were split across names. Fixed with a union-find `dup_group` (§3.1). This changed every grouped number, and all were re-measured: R² 0.849 (was 0.862), brand-held-out 0.76 (was 0.78), Premium interval coverage with a global quantile 0.70 (was 0.64), classifier accuracy 0.866 (was 0.862). |
| `fast_charging_w = NaN` has no JSON form | **Adopted.** Three-state table with `null` as the wire value (§9.3, §9.4). |
| "80% interval" wording | **Adopted.** "Nominal 80% range" plus observed per-band coverage with n, in the UI and the API. The segment gate moved from 0.68 to 0.65, about 2.5 binomial standard errors below nominal at n ≈ 42 (§6.4). |
| `SE = sd / √5` convention | **Adopted: dropped.** Replaced by paired win counts and a pre-declared practical margin δ (§5). |
| "R² > 0.93 means leak" | **Adopted.** Reworded as an audit trigger, with a concrete four-part audit including a label-shuffle test (§5). |
| Value Finder status | **Adopted.** Fixed banner on the view (§7.3). |
| DSA depth | **Partly adopted.** §9.6 records complexity reasoning, and comparables use numpy top-5 selection (verified against scikit-learn). No further custom structures: none is justified at N = 980. |
| "Production-grade" wording | **Adopted.** Positioning sentence in §1.2. |
| No browser tests | **Adopted as optional.** Three Playwright smoke tests via `make smoke`, outside `make ci`, with the manual checklist as the documented fallback (§11). |
| Syllabus-required algorithms | **Adopted.** Gate 0 in §13 and "syllabus-required" rows in the candidate tables (§6.2, §8.2). |

### 16.3 v1.2 to v1.3 (freeze candidate)

| Point | Outcome |
|---|---|
| `RidgeCV` breaks the shared-splits rule | **Adopted.** Tuned `Ridge` (alpha about 11.5, MdAPE 15.9%); `LogisticRegression` `C` is tuned the same way. Re-measured consequence: histogram gradient boosting beats the baseline in 10 of 15 folds (it was 9 against `RidgeCV`), so it passes the gate narrowly. v1.2's sentence saying it fails was wrong and is corrected (§6.3). |
| Test-set rule versus Comparables | **Adopted.** The rule now says "performance-sensitive explainability" and allows descriptive lookups that fit nothing to use the full static data (§5). |
| Bootstrap CIs both required and cuttable | **Adopted.** Optional everywhere; the Models page labels them "omitted" when absent (§5, §10.3, §13.1). |
| ₹40,000 threshold versus ₹40,480 | **Adopted.** Cut-offs stated explicitly; ₹40,480 is the lowest observed Premium price, and any cut-off in (39,999, 40,480] fits the data (§0, §2.1). |
| Positional indices in split tests | **Adopted.** Immutable `row_id` assigned at ingestion and used in every split, group and test (§3.1, §11). |
| "O(1) lookup" for filters | **Adopted.** O(1) on a cache hit, O(N) on a miss (§9.6). |
| Provenance and currency | **Partly adopted.** A "Real World Smartphones Dataset" with 980 phones exists, and a related listing mentions SmartPrix scraping. I could not confirm the original author, the link to v5, or INR from dataset metadata, so INR is marked "supported circumstantially" and the licence "not confirmed" (§2.1, §15). |
| "Nothing in this dataset supports a score that high" | **Adopted.** Removed; the wording is now "a trigger for scrutiny, not proof of leakage" (§6.3). |

### 16.4 v1.3 to v1.3.1 (found while deriving the project documents)

| Point | Outcome |
|---|---|
| Comparables tie-breaking | **Fixed.** `np.argpartition` plus a sort of its five picks is not deterministic under ties: it disagreed with a full stable sort in 468 of 980 queries. The spec now requires `np.partition` for the 5th-smallest distance, keeping every row at or below it, then sorting by (distance, `row_id`) (§6.5, §9.6, §11). |
| Contrast figures and input borders | **Fixed.** Measured contrast replaced the rounded figures (7.1:1 and 6.0:1, not 6.9:1 and 5.9:1). The design file's steel input border is 1.8:1 on white and fails WCAG 1.4.11, so inputs use a graphite border (§10.4, §10.6). `primary-bright` is 4.48:1 on white, so it is for fills only. |
| Effort labels | **Clarified.** The milestone size labels in §13 sum to about 10.5 days, but a bottom-up breakdown into 67 tasks totals about 24 working days (assumed 1.5, 4 and 8 hours for small, medium and large tasks). §13 now says the labels are lower bounds and to use the cut list early if the deadline is short. |