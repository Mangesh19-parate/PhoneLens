# PhoneLens: Memory & Decision Log

## Decisions

### D-23: Mandated Algorithms (G0-01)
- **Status**: Settled
- **Decision**: No additional algorithms mandated by external syllabus/rubric.
- **Suite**: Standard candidate suite defined in `SPEC.md` §6.2 & §8.2.
  - **Regression**: DummyRegressor (median), tuned Ridge, RandomForestRegressor, HistGradientBoostingRegressor.
  - **Classification**: Majority baseline, Regress-then-bin, tuned LogisticRegression, RandomForestClassifier (balanced), HistGradientBoostingClassifier.
