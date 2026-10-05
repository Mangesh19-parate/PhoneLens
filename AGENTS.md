# PhoneLens: Developer & Agent Rules

You are working on **PhoneLens**, an offline-trained smartphone price prediction, market analytics, and segment classification system served via Flask.

## Non-Negotiable Core Rules

1. **Spec is Law**: If any document, test, or code contradicts `SPEC.md`, `SPEC.md` wins. Never edit `SPEC.md` to make failing tests pass.
2. **Leakage Guard**:
   - `price`, `price_segment`, and `rating` MUST NEVER appear in feature lists or input frames for models (`features/spec.py`).
   - The classifier must NEVER receive `price` (it scores 100% artificially, which is a critical bug).
3. **Grouped Validation**:
   - Validation splits, CV folds, and calibration folds MUST ALWAYS use `dup_group` as the grouping key.
   - Never use random k-fold or naive train-test split without grouping (near-duplicate rows leak data).
4. **Single Source of Truth**:
   - Features: Defined only in `src/phonelens/features/spec.py` (`FEATURES`, 23 items).
   - Constants & Thresholds: Defined only in `src/phonelens/config.py`. Never hardcode numbers across modules.
   - Row Identity: `row_id` (0..979) assigned once at ingestion and never reset or modified.
5. **Architectural Isolation**:
   - `webapp/` imports ONLY `phonelens.service.predictor`.
   - `src/` modules NEVER import Flask, `scripts/`, or `webapp/`.
   - Models and features NEVER import Flask.
6. **Persistence & Serialization**:
   - Model bundles (`.joblib`) are plain Python dictionaries of standard scikit-learn / numpy objects. Never pickle custom classes.
   - Offline training only; Flask serves precomputed artifacts and never trains or tunes at request time.
7. **Honesty in Communication & UI**:
   - Interval wording: "Nominal 80% range" (never "80% confidence").
   - Sensitivity wording: Non-causal template only (never "adds", "costs", or "is worth").
   - Value Finder wording: "Listed above/below spec-implied range" (never "bargain" or "overpriced").
   - Static snapshot notice must be present: Static dataset listing prices, assumed INR, not a live price tool.
8. **Git & Verification**:
   - Every task must be verified with tests before marking Done.
   - Update `TRACKER.md` with status and evidence.
   - Record architectural choices or traps in `MEMORY.md`.
