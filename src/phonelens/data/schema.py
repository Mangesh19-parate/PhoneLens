"""Raw dataset schema definition and schema validation."""

import pandas as pd

RAW_COLUMNS: tuple[str, ...] = (
    "brand_name",
    "model",
    "price_segment",
    "price",
    "rating",
    "has_5g",
    "has_nfc",
    "has_ir_blaster",
    "processor_name",
    "processor_brand",
    "num_cores",
    "processor_speed",
    "performance_score",
    "battery_capacity",
    "battery_score",
    "battery_density",
    "battery_type",
    "fast_charging_available",
    "fast_charging",
    "ram_capacity",
    "memory_power",
    "ram_category",
    "internal_memory",
    "storage_category",
    "screen_size",
    "screen_category",
    "display_score",
    "refresh_rate",
    "resolution_width",
    "resolution_height",
    "pixel_per_inches",
    "resolution_type",
    "num_rear_cameras",
    "num_front_cameras",
    "primary_rear_camera_mp",
    "primary_front_camera_mp",
    "total_camera_mp",
    "camera_score",
    "os",
    "extended_memory",
    "extended_upto",
)


def validate_raw(df: pd.DataFrame) -> None:
    """Validate that the DataFrame contains all expected raw columns.

    Raises:
        ValueError: If any required column is missing.
    """
    missing = [col for col in RAW_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Raw dataset is missing required columns: {missing}")
