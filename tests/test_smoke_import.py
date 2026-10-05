"""Smoke import and dataset integrity tests for PhoneLens."""

import importlib

from phonelens.data.load import file_sha256, load_raw


def test_import_phonelens_core():
    """Verify all phonelens modules and subpackages import without errors."""
    modules = [
        "phonelens",
        "phonelens.config",
        "phonelens.data",
        "phonelens.data.load",
        "phonelens.features",
        "phonelens.models",
        "phonelens.analytics",
        "phonelens.service",
    ]
    for mod in modules:
        imported = importlib.import_module(mod)
        assert imported is not None


def test_import_webapp_package():
    """Verify webapp package is importable."""
    import webapp

    assert webapp is not None


def test_config_constants_exist():
    """Verify core constants exist and have expected types."""
    from phonelens import config

    assert config.SEED == 42
    assert config.SEGMENT_LABELS == ("Budget", "Mid-range", "Premium")
    assert config.SEGMENT_EDGES == (20_000, 40_000)
    assert config.OUTER_FOLDS == 5
    assert config.INTERVAL_LEVEL == 0.8


def test_raw_dataset_hash_and_shape():
    """Verify raw dataset checksum and dimensions (980, 41)."""
    expected_hash = "d0816ac9295c8a202c823c5d19df734d15ecb791f81d6a16c52e93f6b4bfbbb1"
    actual_hash = file_sha256()
    assert actual_hash == expected_hash

    df = load_raw()
    assert df.shape == (980, 41)
    assert "price" in df.columns
    assert "price_segment" in df.columns
    assert "brand_name" in df.columns
