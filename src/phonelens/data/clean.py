"""Data cleaning pipeline for PhoneLens.

Implements pure and idempotent transformations:
1. Normalise string columns (strip, lowercase, collapse whitespace).
2. Retain original `model` as `model_display`.
3. Handle sentinels in `fast_charging`: convert to `fast_charging_w` (NaN when <= 0).
4. Assert dataset and domain invariants.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from phonelens.config import CLEAN_CSV, SEGMENT_EDGES, SEGMENT_LABELS


def _normalise_string_series(s: pd.Series) -> pd.Series:
    """Lowercase, strip leading/trailing spaces, and collapse internal whitespace."""
    return s.astype(str).str.strip().str.lower().str.replace(r"\s+", " ", regex=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw smartphone dataset and validate data invariants.

    Parameters:
        df: Raw DataFrame (with row_id assigned at ingestion).

    Returns:
        Cleaned DataFrame.
    """
    out = df.copy()

    # Preserve original model string for presentation
    if "model_display" not in out.columns:
        out["model_display"] = out["model"]

    # Normalise categorical text columns
    text_cols = ["brand_name", "processor_brand", "processor_name", "os"]
    for col in text_cols:
        if col in out.columns:
            out[col] = _normalise_string_series(out[col])

    # Sentinel conversion: fast_charging_w
    # fast_charging == -1 (143 rows): fast charging not available
    # fast_charging == 0 (68 rows): fast charging available, wattage unknown
    cnt_neg1 = (out["fast_charging"] == -1).sum()
    cnt_zero = (out["fast_charging"] == 0).sum()

    # Assert known sentinels on the 980-row dataset
    if len(out) == 980:
        assert cnt_neg1 == 143, f"Expected 143 fast_charging == -1, got {cnt_neg1}"
        assert cnt_zero == 68, f"Expected 68 fast_charging == 0, got {cnt_zero}"

    out["fast_charging_w"] = out["fast_charging"].astype(float)
    out.loc[out["fast_charging_w"] <= 0, "fast_charging_w"] = np.nan

    # Invariant assertions
    assert (out["price"] > 0).all(), "Found non-positive price values"

    # Price segment cut-offs validation
    def _expected_segment(p: float) -> str:
        if p < SEGMENT_EDGES[0]:
            return SEGMENT_LABELS[0]
        if p < SEGMENT_EDGES[1]:
            return SEGMENT_LABELS[1]
        return SEGMENT_LABELS[2]

    computed_segments = out["price"].map(_expected_segment)
    assert (out["price_segment"] == computed_segments).all(), (
        "price_segment column does not match expected threshold cut-offs"
    )

    # Extended memory consistency
    assert (out.loc[~out["extended_memory"], "extended_upto"] == 0).all(), (
        "extended_upto must be 0 when extended_memory is False"
    )

    # RAM capacity physically valid
    assert (out["ram_capacity"] >= 1).all() and (out["ram_capacity"] <= 18).all(), (
        "ram_capacity outside expected [1, 18] range"
    )

    return out


def write_clean(df: pd.DataFrame, path: str | Path | None = None) -> None:
    """Save cleaned DataFrame to CSV without index."""
    target_path = Path(path) if path is not None else CLEAN_CSV
    target_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_path, index=False)
