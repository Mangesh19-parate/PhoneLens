"""Raw dataset loading and integrity verification."""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from phonelens.config import RAW_CSV
from phonelens.data.schema import validate_raw


def file_sha256(path: str | Path | None = None) -> str:
    """Compute and return the SHA-256 hex digest for a given file."""
    target_path = Path(path) if path is not None else RAW_CSV
    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    hasher = hashlib.sha256()
    with open(target_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_raw(path: str | Path | None = None) -> pd.DataFrame:
    """Load the raw smartphone dataset as a pandas DataFrame with validated schema and row_id.

    Assigns immutable row_id (0..N-1) at ingestion in raw CSV order.
    """
    target_path = Path(path) if path is not None else RAW_CSV
    if not target_path.exists():
        raise FileNotFoundError(f"Raw CSV not found: {target_path}")

    df = pd.read_csv(target_path)
    validate_raw(df)

    # Assign row_id once at ingestion if not already present
    if "row_id" not in df.columns:
        df.insert(0, "row_id", np.arange(len(df), dtype=int))
    return df
