"""Central configuration for PhoneLens.

Single source of truth for all constants, thresholds, paths, and hyperparameters.
No module in the project may hardcode these values elsewhere.
"""

from pathlib import Path

# Paths
ROOT_DIR: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = ROOT_DIR / "data"
RAW_CSV: Path = DATA_DIR / "raw" / "smartphone_v5.csv"
CLEAN_CSV: Path = DATA_DIR / "processed" / "phones_clean.csv"
ARTIFACTS_DIR: Path = ROOT_DIR / "artifacts"
REPORTS_DIR: Path = ROOT_DIR / "reports"

# Random Seeds
SEED: int = 42
SEARCH_SEED: int = 42
CV_SEEDS: tuple[int, ...] = (11, 22, 33)
CAL_SEED: int = 5

# Splitting & Cross Validation
OUTER_FOLDS: int = 5
SEARCH_ITER: int = 25

# Preprocessing & Encoders
ENCODER_MIN_FREQUENCY: int = 5

# Market Segments & Interval Bands
SEGMENT_LABELS: tuple[str, ...] = ("Budget", "Mid-range", "Premium")
SEGMENT_EDGES: tuple[int, int] = (20_000, 40_000)
BAND_LABELS: tuple[str, ...] = ("A", "B", "C")
INTERVAL_LEVEL: float = 0.8
BAND_MIN_RESIDUALS: int = 50
MAINSTREAM_MAX_PRICE: int = 150_000

# Analytics
MIN_GROUP_N: int = 10
TOP_BRANDS: int = 12

# Model Selection Margins & Rules
DELTA_MDAPE: float = 0.005
DELTA_MACRO_F1: float = 0.01
CALIB_LOGLOSS_MARGIN: float = 0.005
BASELINE_MIN_WINS: int = 10

# Quality Gates & Scrutiny Triggers
GATE_TEST_MDAPE_MAX: float = 0.16
GATE_TEST_R2_MIN: float = 0.82
R2_AUDIT_TRIGGER: float = 0.93
GATE_COVERAGE_OVERALL: tuple[float, float] = (0.72, 0.88)
GATE_COVERAGE_SEGMENT_MIN: float = 0.65
GATE_MACRO_F1_MIN: float = 0.80
ACC_AUDIT_TRIGGER: float = 0.97
SHUFFLE_R2_MAX: float = 0.05
SHUFFLE_ACC_MARGIN: float = 0.05
LATENCY_P95_MS: int = 150

# Web, Inference & Explainability
MAX_BODY_BYTES: int = 16 * 1024  # 16 KB body limit
SENSITIVITY_TOP_K: int = 8
COMPARABLES_K: int = 5
PERM_REPEATS: int = 10
BOOTSTRAP_RESAMPLES: int = 1000
APPLE_PROCESSOR_BRANDS: frozenset[str] = frozenset({"bionic", "fusion"})
VERSION_OVERRIDE_ENV: str = "PHONELENS_ALLOW_VERSION_MISMATCH"
