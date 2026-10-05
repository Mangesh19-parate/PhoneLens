"""Smoke import tests for PhoneLens packages."""

import importlib


def test_import_phonelens_core():
    """Verify all phonelens modules and subpackages import without errors."""
    modules = [
        "phonelens",
        "phonelens.config",
        "phonelens.data",
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
