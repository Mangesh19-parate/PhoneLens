# PhoneLens: Memory & Decision Log

## Decisions

### D-23: Mandated Algorithms (G0-01)
- **Status**: Settled
- **Decision**: No additional algorithms mandated by external syllabus/rubric.
- **Suite**: Standard candidate suite defined in `SPEC.md` §6.2 & §8.2.
  - **Regression**: DummyRegressor (median), tuned Ridge, RandomForestRegressor, HistGradientBoostingRegressor.
  - **Classification**: Majority baseline, Regress-then-bin, tuned LogisticRegression, RandomForestClassifier (balanced), HistGradientBoostingClassifier.

### D-24: Target Environment & Host Platform (G0-02)
- **Status**: Verified
- **OS**: Windows 11 AMD64 (PowerShell / `python -m` commands used as standard CLI interface).
- **Python**: Python 3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)].
- **Installed Packages**:
  - Flask: 3.1.3
  - scikit-learn: 1.9.0
  - pandas: 3.0.3
  - numpy: 2.4.6
  - joblib: 1.4.2
  - pydantic: 2.8.2 (pydantic-core: 2.20.1)
  - pytest: 9.1.1
  - pytest-cov: 7.1.0 (coverage: 7.15.2)
  - ruff: 0.5.6
- **Result**: Dry-run install and package import checks passed with zero errors.
