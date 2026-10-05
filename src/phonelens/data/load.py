"""Raw dataset loading and integrity verification."""

import hashlib
from pathlib import Path

import pandas as pd

from phonelens.config import RAW_CSV


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
    """Load the raw smartphone dataset as a pandas DataFrame."""
    target_path = Path(path) if path is not None else RAW_CSV
    if not target_path.exists():
        raise FileNotFoundError(f"Raw CSV not found: {target_path}")
    return pd.read_csv(target_path)
