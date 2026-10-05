"""Tests for data loading, schema validation, and cleaning."""

import numpy as np
import pandas as pd
import pytest
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
    assert len(df.columns) == 42  # 41 raw columns + 1 row_id
