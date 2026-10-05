# PhoneLens

> Smartphone price estimation, market analytics, and segment classification with truthful uncertainty, built with Flask and scikit-learn.

---

## 1. Dataset Provenance & Attribution

- **File**: `data/raw/smartphone_v5.csv` (980 rows × 41 columns)
- **SHA-256**: `d0816ac9295c8a202c823c5d19df734d15ecb791f81d6a16c52e93f6b4bfbbb1`
- **Currency Assumption**: Indian Rupee (INR, ₹). Supported by Indian market brand distributions (iQOO, Poco, Tecno, Infinix, Lyf) and price distributions matching historical Indian retail/SmartPrix listings.
- **Licence & Terms**: Sourced from public academic/educational smartphone datasets (e.g. Kaggle/Gigasheet smartphone dataset variants). Upstream licence is not explicitly confirmed; treated strictly as an educational/research benchmark snapshot.
- **Caveat & Static Snapshot Notice**: All prices represent static historical listing prices, not live market retail prices.

---

## 2. Quickstart & Command Table

| Target (Linux/Make) | Windows Command (PowerShell) | Description |
|---|---|---|
| `make setup` | `python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt -r requirements-dev.txt` | Set up virtual environment and install dependencies |
| `make data` | `python -m scripts.clean_data` | Clean raw data, run duplicate audit, and generate `phones_clean.csv` |
| `make train` | `python -m scripts.train` | Train regression and classification models, calibrate, and save bundles |
| `make evaluate` | `python -m scripts.evaluate` | Evaluate on locked test set and generate `metrics.json` & `model_card.md` |
| `make analytics` | `python -m scripts.build_analytics` | Build out-of-fold predictions and `analytics.json` |
| `make run` | `flask --app webapp run` | Run local web application |
| `make test` | `pytest --cov=src --cov-report=term-missing` | Run test suite with coverage |
| `make lint` | `ruff check . ; ruff format --check .` | Lint and style checking |
| `make ci` | `ruff check . ; pytest --cov=src` | Full CI verification pass |
