"""Tests for data loading, schema validation, and cleaning pipeline."""

import numpy as np
import pandas as pd
import pytest
from phonelens.data.clean import clean, write_clean
from phonelens.data.load import load_raw
from phonelens.data.schema import RAW_COLUMNS, validate_raw


def test_validate_raw_success():
    """Verify that a DataFrame with all raw columns passes validation."""
    df = pd.DataFrame(columns=list(RAW_COLUMNS))
    validate_raw(df)


def test_validate_raw_missing_column_raises():
    """Verify that missing columns raise ValueError."""
    df = pd.DataFrame(columns=["brand_name", "model", "price"])
    with pytest.raises(ValueError, match="Raw dataset is missing required columns"):
        validate_raw(df)


def test_load_raw_assigns_row_id():
    """Verify load_raw attaches contiguous row_id from 0 to 979."""
    df = load_raw()
    assert "row_id" in df.columns
    assert df.columns[0] == "row_id"
    assert (df["row_id"].to_numpy() == np.arange(980)).all()
    assert len(df) == 980
    assert len(df.columns) == 42


def test_clean_idempotence():
    """Verify clean(df) is pure and idempotent."""
    raw_df = load_raw()
    cleaned_first = clean(raw_df)
    cleaned_second = clean(cleaned_first)

    pd.testing.assert_frame_equal(cleaned_first, cleaned_second)


def test_clean_sentinels_and_invariants():
    """Verify fast_charging_w sentinels and invariant checks in cleaned frame."""
    raw_df = load_raw()
    cleaned = clean(raw_df)

    assert "fast_charging_w" in cleaned.columns
    assert cleaned["fast_charging_w"].isna().sum() == 143 + 68
    assert "model_display" in cleaned.columns
    assert (cleaned["price"] > 0).all()
    assert (cleaned["ram_capacity"] >= 1).all() and (cleaned["ram_capacity"] <= 18).all()


def test_write_clean_round_trip(tmp_path):
    """Verify write_clean writes a valid CSV file."""
    raw_df = load_raw()
    cleaned = clean(raw_df)
    out_file = tmp_path / "phones_clean_test.csv"
    write_clean(cleaned, path=out_file)

    assert out_file.exists()
    reloaded = pd.read_csv(out_file)
    assert len(reloaded) == len(cleaned)
