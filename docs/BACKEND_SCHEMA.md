# PhoneLens: Backend Schema

| | |
|---|---|
| Version | 1.0 |
| Date | 2026-10-04 |
| Derived from | `spec.md` v1.3.2 |
| Rule | If this document and `spec.md` disagree, `spec.md` wins. Anything marked **Implementation choice** fills a gap the spec leaves open. |

---

## 1. Scope

PhoneLens has no database. The "backend schema" is therefore the set of data shapes that move through the system: the raw CSV, the cleaned frame, the 23-feature model contract, the API request and response bodies, the analytics payloads, and the artifact files. This document defines each one.

Conventions:

| Item | Convention |
|---|---|
| Field names | `snake_case` everywhere, identical in CSV, Python, JSON and query strings |
| Money | INR, integers in API responses; formatted in the browser with `Intl.NumberFormat("en-IN", ...)` |
| Missing numbers | `null` on the wire; NaN inside models. JSON has no NaN. |
| Ratios | Fractions from 0 to 1 on the wire; the UI formats percentages |
| Time | ISO 8601 UTC strings; `model.version` is the training date `YYYY-MM-DD` |
| Row identity | `row_id`, an integer from 0 to 979 assigned at ingestion, never reset |
| Class order | Budget, Mid-range, Premium |

## 2. Raw dataset schema (`data/raw/smartphone_v5.csv`)

980 rows, 41 columns, no nulls, no duplicate rows, 980 unique `model` strings. Values below were measured on the shipped file.

| # | Column | Type | Observed | Meaning | Disposition | Cleaning or note |
|---|---|---|---|---|---|---|
| 1 | brand_name | str | 46 values | Manufacturer | Feature (categorical) | Lowercase, trim. Also in `spec_fingerprint`. |
| 2 | model | str | 980 unique | Listing name, sometimes with a parenthesised RAM/storage tag | Identifier | Kept as `model_display`; `base_model` derived for grouping. |
| 3 | price_segment | str | Budget 506, Mid-range 263, Premium 211 | Price bin | **Target (classifier).** Never a feature | Checked against the 20,000 and 40,000 cut-offs. |
| 4 | price | int | 3,499 to 650,000; median 19,994.5 | Listed price, INR assumed | **Target (regressor).** Never a feature of the classifier | Must be above 0. Model target is `log1p(price)`. |
| 5 | rating | int | 60 to 89 | Post-launch rating | Excluded | Not a predictor (unknown at pricing time). |
| 6 | has_5g | bool | True 549 / False 431 | 5G support | Feature (binary) | Cast to int for models. |
| 7 | has_nfc | bool | True 393 / False 587 | NFC | Feature (binary) | Cast to int. |
| 8 | has_ir_blaster | bool | True 159 / False 821 | IR blaster | Feature (binary) | Cast to int. |
| 9 | processor_name | str | 214 raw, 149 after cleanup | Chipset name | Analytics and display only; in `spec_fingerprint` | Lowercase, trim, collapse whitespace (311 rows had double spaces). |
| 10 | processor_brand | str | 13 values | Chipset family | Feature (categorical) | Lowercase, trim. Over all 980 rows, 4 values have fewer than 5 rows: spreadtrum, sc9863a, fusion, mediatek. |
| 11 | num_cores | int | 4, 6, 8 | CPU cores | Feature | In `spec_fingerprint`. |
| 12 | processor_speed | int | 1, 2, 3 | CPU speed, truncated GHz | Feature (tier) | Labelled "CPU speed tier". |
| 13 | performance_score | int | 4 to 25 | Engineered upstream | Excluded | Unknown provenance; no measurable gain. May appear in analytics as "as published in dataset". |
| 14 | battery_capacity | int | 1,821 to 22,000 mAh | Battery | Feature | In `spec_fingerprint`. |
| 15 | battery_score | int | −8,000 to 1,104,000 | `battery_capacity × fast_charging` | Dropped | Exact product, negative for 143 rows, 0 for 68. |
| 16 | battery_density | int | 387 to 3,343 | Engineered upstream | Excluded | Unknown provenance. |
| 17 | battery_type | str | Small, Medium, Large | Binned battery capacity | Dropped | Binned copy of a raw column. |
| 18 | fast_charging_available | bool | True 837 / False 143 | Fast charging supported | Feature (binary) | Kept as is. |
| 19 | fast_charging | int | −1 to 240 | Charging wattage with sentinels | Converted | −1 (143 rows) means unavailable; 0 (68 rows) means available, wattage unknown. Becomes `fast_charging_w`. Raw value is in `spec_fingerprint`. |
| 20 | ram_capacity | int | 1 to 18 GB; 9 distinct | RAM | Feature | Not in `spec_fingerprint`. |
| 21 | memory_power | int | 8 to 12,288 | `ram × storage` | Dropped | Exact arithmetic on raw columns. |
| 22 | ram_category | str | 3 values | Binned RAM | Dropped | Binned copy. |
| 23 | internal_memory | int | 8 to 1,024 GB; 8 distinct | Storage | Feature | Not in `spec_fingerprint`. |
| 24 | storage_category | str | 3 values | Binned storage | Dropped | Binned copy. |
| 25 | screen_size | int | 3 to 8 | Integer inches | Dropped | 931 of 980 rows equal 6; no signal. |
| 26 | screen_category | str | 3 values | Derived from `screen_size` | Dropped | Derived from a truncated column. |
| 27 | display_score | int | 11,755 to 109,336 | Engineered upstream | Excluded | Unknown provenance. May appear in analytics as published. |
| 28 | refresh_rate | int | 60 to 240 Hz; 6 distinct | Refresh rate | Feature | In `spec_fingerprint`. |
| 29 | resolution_width | int | 480 to 2,460 | Pixels | Feature | In `spec_fingerprint`. |
| 30 | resolution_height | int | 480 to 3,840 | Pixels | Feature | In `spec_fingerprint`. |
| 31 | pixel_per_inches | int | 195 to 642 | Pixel density | Feature | Filled by the resolution preset in the form. |
| 32 | resolution_type | str | 3 values | Label such as Ultra HD | Dropped | Mislabelled: "Ultra HD" is assigned to 589 rows with 1080-pixel width. |
| 33 | num_rear_cameras | int | 1 to 4 | Rear cameras | Feature | In `spec_fingerprint`. |
| 34 | num_front_cameras | int | 1, 2 | Front cameras | Feature | Not in `spec_fingerprint`. |
| 35 | primary_rear_camera_mp | int | 2 to 200 | Main rear camera MP | Feature | In `spec_fingerprint`. |
| 36 | primary_front_camera_mp | int | 1 to 60 | Front camera MP | Feature | In `spec_fingerprint`. |
| 37 | total_camera_mp | int | 5 to 260 | `rear_mp + front_mp` | Dropped | Exact arithmetic. |
| 38 | camera_score | int | 2 to 800 | `rear_mp × num_rear_cameras` | Dropped | Exact arithmetic. |
| 39 | os | str | android 923, ios 46, other 11 | Operating system | Feature (**strict enum**) | Lowercase, trim. In `spec_fingerprint`. |
| 40 | extended_memory | bool | True 618 / False 362 | Expandable storage | Feature (binary) | Must be consistent with `extended_upto`. |
| 41 | extended_upto | int | 0 to 2,048 GB | Maximum expansion | Feature | 0 whenever `extended_memory` is false (asserted). |

Counts by disposition: 22 raw columns used as features, 2 targets, 1 identifier, and 16 columns that are dropped, excluded, analytics-only or converted (22 + 2 + 1 + 16 = 41). The 23rd model feature, `fast_charging_w`, is derived from `fast_charging`. `spec.md` §3.3 is authoritative.

## 3. Cleaned frame (`data/processed/phones_clean.csv`)

Output of `clean()`. Pure and idempotent. Written as CSV (no `pyarrow`). Under pandas 3, string columns use the `str` dtype.

| Added or changed | Type | Definition |
|---|---|---|
| `row_id` | int | `np.arange(len(df))` at ingestion; first column |
| `model_display` | str | Original `model` string |
| `brand_name`, `processor_brand`, `processor_name`, `os` | str | Lowercase, stripped, internal whitespace collapsed |
| `base_model` | str | Lowercase `model` with parenthesised text removed, whitespace collapsed |
| `spec_fingerprint` | str | Joined values of `brand_name`, normalised `processor_name`, `battery_capacity`, `fast_charging`, `refresh_rate`, `resolution_width`, `resolution_height`, `num_rear_cameras`, `primary_rear_camera_mp`, `primary_front_camera_mp`, `has_5g`, `has_nfc`, `has_ir_blaster`, `os`, `num_cores`, `processor_speed`. Excludes RAM, storage and expandable storage. |
| `dup_group` | int | Union-find root (lowest `row_id`) over shared `base_model` or `spec_fingerprint` |
| `fast_charging_w` | float | NaN where `fast_charging <= 0` |

Invariants asserted by `clean()`: `price > 0`; `price_segment` matches the cut-offs; `extended_upto == 0` whenever `extended_memory` is false; `ram_capacity` between 1 and 18; `row_id` is unique and contiguous. Counts logged: 143 rows at −1, 68 rows at 0.

## 4. Model feature contract

23 columns. Defined once in `features/spec.py`; the API schema, form, regressor and classifier all derive from it. Hard bounds other than battery, RAM, refresh rate and fast-charging wattage are an **implementation choice**, set wider than the training range so only impossible values are rejected.

| Feature | Type | Hard bounds (422 outside) | NaN | Importance group | Training range or values (all 980 rows) | Form control |
|---|---|---|---|---|---|---|
| brand_name | categorical | free string, 1–40 chars | no | brand | 46 values (xiaomi 134, samsung 132, vivo 111, realme 97, oppo 88 lead) | Dropdown from fitted encoder, plus Other |
| processor_brand | categorical | free string, 1–40 chars | no | processor | 13 values | Dropdown |
| os | categorical | enum: android, ios, other | no | brand | android 923, ios 46, other 11 | Dropdown |
| has_5g | binary | bool | no | connectivity | — | Toggle |
| has_nfc | binary | bool | no | connectivity | — | Toggle |
| has_ir_blaster | binary | bool | no | connectivity | — | Toggle |
| num_cores | integer | 2–16 | no | processor | 4, 6, 8 | Dropdown 4, 6, 8 |
| processor_speed | integer | 1–5 | no | processor | 1, 2, 3 | Segmented control (CPU speed tier) |
| ram_capacity | integer, GB | 1–24 | no | memory | 1–18; 1, 2, 3, 4, 6, 8, 12, 16, 18 | Dropdown of training values |
| internal_memory | integer, GB | 1–4096 | no | memory | 8–1,024; 8, 16, 32, 64, 128, 256, 512, 1024 | Dropdown of training values |
| extended_memory | binary | bool | no | memory | — | Toggle |
| extended_upto | integer, GB | 0–4096; must be 0 if extended_memory is false | no | memory | 0, 32, 64, 128, 256, 512, 1024, 2048 | Dropdown shown only when the toggle is on |
| battery_capacity | integer, mAh | 1,000–25,000 | no | battery | 1,821–22,000; median 5,000 | Number input |
| fast_charging_available | binary | bool | no | battery | — | Three-way choice, part 1 |
| fast_charging_w | integer, W | 5–240; null allowed | **yes (null becomes NaN)** | battery | 10–240; median 33 | Three-way choice, part 2 |
| refresh_rate | integer, Hz | 30–240 | no | display | 60, 90, 120, 144, 165, 240 | Dropdown |
| resolution_width | integer, px | 240–4000 | no | display | 480–2,460 | Resolution preset |
| resolution_height | integer, px | 240–6000 | no | display | 480–3,840 | Resolution preset |
| pixel_per_inches | integer | 100–1000 | no | display | 195–642; median 397 | Resolution preset, editable under Advanced |
| num_rear_cameras | integer | 1–6 | no | camera | 1–4 | Stepper |
| num_front_cameras | integer | 1–4 | no | camera | 1–2 | Stepper |
| primary_rear_camera_mp | integer, MP | 1–300 | no | camera | 2–200; median 50 | Number input |
| primary_front_camera_mp | integer, MP | 1–120 | no | camera | 1–60; median 16 | Number input |

`FORBIDDEN_FEATURES = {"price", "price_segment", "rating", "model", "battery_score", "memory_power", "camera_score", "total_camera_mp", "performance_score", "display_score", "battery_density", "screen_size", "screen_category", "resolution_type", "ram_category", "storage_category", "battery_type", "processor_name"}`. `test_no_leakage` fails if any appear in `FEATURES`. Importance groups are an **implementation choice** that maps the spec's seven groups onto the 23 features.

Fast charging has three states and both fields are always sent:

| State | `fast_charging_available` | `fast_charging_w` | Model input |
|---|---|---|---|
| No fast charging | `false` | `null` | NaN |
| Yes, wattage known | `true` | a number, 5–240 | the number |
| Yes, wattage unknown | `true` | `null` | NaN |

Category statuses, taken from the fitted encoder: `known` (frequent), `rare` (seen fewer than 5 times, infrequent bucket), `unseen` (never seen, infrequent bucket). `os` is the only strict enum.

## 5. Constants (`config.py`)

Every threshold and margin lives here once. `test_import_graph.py` fails if another module hard-codes one.

| Constant | Value | Used for |
|---|---|---|
| SEED | 42 | Global seed |
| OUTER_FOLDS | 5 | Outer StratifiedGroupKFold folds; first fold is test |
| CV_SEEDS | (11, 22, 33) | Three repeats of five folds give CV_SPLITS |
| CAL_SEED | 5 | Seed for CAL_SPLITS |
| SEARCH_ITER | 25 | RandomizedSearchCV n_iter |
| SEARCH_SEED | 42 | RandomizedSearchCV random_state |
| ENCODER_MIN_FREQUENCY | 5 | OneHotEncoder min_frequency; also the rare-category threshold |
| SEGMENT_LABELS | ('Budget', 'Mid-range', 'Premium') | Ordered classes |
| SEGMENT_EDGES | (20_000, 40_000) | Budget below 20,000; Premium at or above 40,000 |
| BAND_LABELS | ('A', 'B', 'C') | Interval bands, same edges |
| INTERVAL_LEVEL | 0.8 | Nominal level |
| BAND_MIN_RESIDUALS | 50 | Below this, a band uses the global quantile |
| MAINSTREAM_MAX_PRICE | 150000 | MAE on mainstream rows; Value Finder default exclusion |
| MIN_GROUP_N | 10 | Suppression threshold in analytics |
| TOP_BRANDS | 12 | Brand filter size before Other |
| DELTA_MDAPE | 0.005 | Practical margin for regression selection and the baseline gate |
| DELTA_MACRO_F1 | 0.01 | Practical margin for classification selection and the baseline gate |
| CALIB_LOGLOSS_MARGIN | 0.005 | A difference below this goes to the uncalibrated model |
| BASELINE_MIN_WINS | 10 | Folds out of 15 where the selected model must beat Ridge on MdAPE |
| GATE_TEST_MDAPE_MAX | 0.16 | QG-02 |
| GATE_TEST_R2_MIN | 0.82 | QG-02 |
| R2_AUDIT_TRIGGER | 0.93 | QG-03 |
| GATE_COVERAGE_OVERALL | (0.72, 0.88) | QG-04 |
| GATE_COVERAGE_SEGMENT_MIN | 0.65 | QG-04 |
| GATE_MACRO_F1_MIN | 0.8 | QG-05 |
| ACC_AUDIT_TRIGGER | 0.97 | QG-06 |
| SHUFFLE_R2_MAX | 0.05 | Label-shuffle test, regression |
| SHUFFLE_ACC_MARGIN | 0.05 | Label-shuffle test: majority rate plus this |
| LATENCY_P95_MS | 150 | QG-10 |
| MAX_BODY_BYTES | 16 * 1024 | 413 above this |
| SENSITIVITY_TOP_K | 8 | Variants scored per request |
| COMPARABLES_K | 5 | Neighbours returned |
| PERM_REPEATS | 10 | Permutation importance repeats |
| BOOTSTRAP_RESAMPLES | 1000 | Optional CIs |
| APPLE_PROCESSOR_BRANDS | {'bionic', 'fusion'} | Soft-warning rule for os = ios; values observed on the 46 ios rows |
| VERSION_OVERRIDE_ENV | 'PHONELENS_ALLOW_VERSION_MISMATCH' | Version guard override |

## 6. API schemas

### 6.1 Request: `PhoneSpec`

Used by `POST /api/predict` and `POST /api/classify`. Tested against pydantic 2.13.5 for these cases: valid body; the three fast-charging states; `os` outside the enum; cross-field violations naming the dependent field; missing key (including `fast_charging_w`, which must be present but may be `null`); float for an integer; a string for a boolean; an unknown extra key; an unseen brand (accepted). `extra="forbid"` and `StrictInt`/`StrictBool` are **implementation choices**.

```python
"""webapp/schemas.py (sketch, tested against pydantic 2.13.5)."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import (BaseModel, ConfigDict, Field, StrictBool, StrictInt,
                      ValidationError, ValidationInfo, field_validator)

# Physical bounds: hard 422 outside these. Only battery, RAM, refresh rate and
# fast-charging wattage come from the spec; the rest are implementation choices,
# set wider than the training range so that only impossible values are rejected.
BOUNDS = {
    "num_cores": (2, 16), "processor_speed": (1, 5),
    "ram_capacity": (1, 24), "internal_memory": (1, 4096), "extended_upto": (0, 4096),
    "battery_capacity": (1000, 25000), "fast_charging_w": (5, 240),
    "refresh_rate": (30, 240),
    "resolution_width": (240, 4000), "resolution_height": (240, 6000),
    "pixel_per_inches": (100, 1000),
    "num_rear_cameras": (1, 6), "num_front_cameras": (1, 4),
    "primary_rear_camera_mp": (1, 300), "primary_front_camera_mp": (1, 120),
}
Os = Literal["android", "ios", "other"]


def _b(name):                                   # Field with the central bounds
    lo, hi = BOUNDS[name]
    return Field(ge=lo, le=hi)


class PhoneSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    brand_name: str = Field(min_length=1, max_length=40)        # constrained string, not an enum
    processor_brand: str = Field(min_length=1, max_length=40)   # constrained string, not an enum
    os: Os                                                      # the only strict enum
    has_5g: StrictBool
    has_nfc: StrictBool
    has_ir_blaster: StrictBool
    num_cores: StrictInt = _b("num_cores")
    processor_speed: StrictInt = _b("processor_speed")
    ram_capacity: StrictInt = _b("ram_capacity")
    internal_memory: StrictInt = _b("internal_memory")
    extended_memory: StrictBool
    extended_upto: StrictInt = _b("extended_upto")              # must be 0 when extended_memory is false
    battery_capacity: StrictInt = _b("battery_capacity")
    fast_charging_available: StrictBool
    fast_charging_w: Optional[StrictInt] = Field(...)           # required key, null allowed
    refresh_rate: StrictInt = _b("refresh_rate")
    resolution_width: StrictInt = _b("resolution_width")
    resolution_height: StrictInt = _b("resolution_height")
    pixel_per_inches: StrictInt = _b("pixel_per_inches")
    num_rear_cameras: StrictInt = _b("num_rear_cameras")
    num_front_cameras: StrictInt = _b("num_front_cameras")
    primary_rear_camera_mp: StrictInt = _b("primary_rear_camera_mp")
    primary_front_camera_mp: StrictInt = _b("primary_front_camera_mp")

    @field_validator("brand_name", "processor_brand", "os", mode="before")
    @classmethod
    def _lower(cls, v):
        return v.strip().lower() if isinstance(v, str) else v

    # Cross-field rules sit on the dependent field so the error names that field.
    @field_validator("extended_upto")
    @classmethod
    def _extended(cls, v, info: ValidationInfo):
        if info.data.get("extended_memory") is False and v != 0:
            raise ValueError("must be 0 when extended_memory is false")
        return v

    @field_validator("fast_charging_w")
    @classmethod
    def _fast_charging(cls, v, info: ValidationInfo):
        if info.data.get("fast_charging_available") is False and v is not None:
            raise ValueError("must be null when fast_charging_available is false")
        if v is not None and not (BOUNDS["fast_charging_w"][0] <= v <= BOUNDS["fast_charging_w"][1]):
            raise ValueError("must be between 5 and 240")
        return v


def to_error_fields(exc: ValidationError) -> dict[str, str]:
    """Map pydantic errors to the spec's one error shape: {field: message}."""
    fields: dict[str, str] = {}
    for e in exc.errors():
        name = str(e["loc"][0]) if e["loc"] else "_body"
        typ = e["type"]
        if typ in ("greater_than_equal", "less_than_equal") and name in BOUNDS:
            lo, hi = BOUNDS[name]
            msg = f"must be between {lo} and {hi}"
        elif typ == "missing":
            msg = "is required"
        elif typ == "extra_forbidden":
            msg = "is not an accepted field"
        elif typ == "literal_error":
            msg = "must be one of " + ", ".join(e["ctx"]["expected"].replace("'", "").split(" or "))
        elif typ.endswith("_type") or typ == "bool_type":
            msg = "has the wrong type"
        elif typ == "value_error":
            msg = str(e["msg"]).removeprefix("Value error, ")
        else:
            msg = e["msg"]
        fields.setdefault(name, msg)
    return fields


def error_body(fields: dict[str, str]) -> dict:
    return {"error": {"code": "validation_error", "message": "Invalid input", "fields": fields}}


def fast_charging_state(spec: PhoneSpec) -> str:
    if not spec.fast_charging_available:
        return "none"
    return "known" if spec.fast_charging_w is not None else "unknown"
```

Error body (the one shape, `spec.md` §9.3):

```json
{ "error": { "code": "validation_error", "message": "Invalid input", "fields": { "ram_capacity": "must be between 1 and 24" } } }
```

| Status | `error.code` | When |
|---|---|---|
| 400 | `bad_json` | Body is not valid JSON |
| 404 | `not_found` | Unknown `/api/*` route (JSON, not HTML) |
| 413 | `payload_too_large` | Body over 16 KB |
| 422 | `validation_error` | Schema or cross-field failure; `fields` lists each offender |
| 500 | `internal_error` | Unexpected failure; body also carries `request_id` (**implementation choice** for the field name) |

### 6.2 Response: `POST /api/predict`

```json
{
  "currency": "INR",
  "price": 21400,
  "interval": { "nominal_level": 0.8, "method": "per_band_residual", "low": 15900, "high": 28700,
    "observed_coverage": { "band": "B", "coverage": 0.84, "n": 52, "overall": 0.82 } },
  "sensitivity": [
    { "feature": "ram_capacity", "label": "RAM", "submitted": 8, "median": 6, "delta_price": -2100,
      "text": "Setting RAM to the dataset median (6 GB) instead of your 8 GB changes this model's estimate by -₹2,100." }
  ],
  "comparables": [ { "model": "Example Phone 5G", "price": 22999, "differs": ["ram_capacity", "refresh_rate"] } ],
  "category_status": { "brand_name": "known", "processor_brand": "known" },
  "warnings": ["battery_capacity is above the training range (max 22000)"],
  "model": { "name": "random_forest", "version": "2026-09-30", "trained_at": "2026-09-30T10:00:00Z" }
}
```

| Field | Type | Notes |
|---|---|---|
| `price` | int | `round(expm1(z_hat))` |
| `interval.low`, `interval.high` | int | `expm1(z_hat ∓ q_band)`, rounded; `low` clipped at 0 |
| `interval.observed_coverage` | object | `band` is the request's band (A, B or C); values come from `metrics.json`; `coverage` and `overall` are fractions; `n` is the test rows in that band |
| `sensitivity` | array of 8 | One per top numeric feature; `text` from the single template |
| `comparables` | array of 5 | `differs` lists feature names whose values differ from the request |
| `category_status` | object | One of `known`, `rare`, `unseen` per category field |
| `warnings` | array of string | Templates in section 7 |
| `model` | object | `name`, `version`, `trained_at` |

### 6.3 Response: `POST /api/classify`

```json
{
  "segment": "Mid-range",
  "probabilities": { "Budget": 0.18, "Mid-range": 0.71, "Premium": 0.11 },
  "regressor_segment": "Mid-range",
  "borderline": false,
  "comparables": [ ],
  "category_status": { "brand_name": "known", "processor_brand": "known" },
  "warnings": [ ],
  "model": { "name": "random_forest", "calibration": "none", "version": "2026-09-30" }
}
```

`model.calibration` is `none` or `sigmoid_grouped`. The UI caption follows it. `borderline` is true when `segment != regressor_segment`, or when the 80% range contains 20,000 or 40,000 in its interior (`low < t <= high`).

### 6.4 `GET /api/meta/options` (**implementation choice** for the exact shape)

```json
{
  "currency": "INR",
  "categories": {
    "brand_name": { "values": ["apple", "iqoo", "xiaomi"], "other_label": "Other" },
    "processor_brand": { "values": ["bionic", "snapdragon"], "other_label": "Other" },
    "os": { "values": ["android", "ios", "other"] }
  },
  "numeric": {
    "ram_capacity": { "allowed": [1, 2, 3, 4, 6, 8, 12, 16, 18], "min": 1, "max": 18, "median": 6 },
    "battery_capacity": { "min": 1821, "max": 22000, "median": 5000 }
  },
  "resolution_presets": [
    { "id": "fhd_plus", "label": "FHD+ 1080 × 2400", "resolution_width": 1080, "resolution_height": 2400, "pixel_per_inches": 399 }
  ],
  "presets": [
    { "id": "mid_range", "label": "Mid-range", "model_display": "Example Phone 5G", "spec": { "...": "a full PhoneSpec body" } }
  ],
  "default_preset": "mid_range"
}
```

Brand and processor lists come from the fitted encoder (`categories_` minus `infrequent_categories_`), never from the full CSV. Numeric ranges and medians come from the training rows. Presets (Budget, Mid-range, Flagship) are real rows chosen by rule: the row nearest each segment's median on the numeric features. Resolution presets are chosen by rule: for each width with at least 30 phones, the most frequent height with its median pixel density. On the shipped data that gives 720 × 1600 (149 phones, ppi 269), 1080 × 2400 (342, ppi 399) and 1440 × 3200 (31, ppi 521); labels HD+, FHD+ and QHD+ are mapped from width.

### 6.5 Other endpoints

| Endpoint | Response |
|---|---|
| `GET /healthz` | `{ "status": "ok", "model_version": "...", "trained_at": "...", "guard": "ok" or "mismatch_overridden", "versions": { "python": "3.12.3", "scikit_learn": "1.8.0", "pandas": "3.0.2", "numpy": "2.4.4", "joblib": "..." } }` |
| `GET /api/models/metrics` | The contents of `metrics.json` (section 9.5) |
| `GET /api/analytics/<view_id>` | The envelope in section 8 |

## 7. Warning catalogue

Warnings are plain strings in `warnings`. Templates:

| Case | Message template | Trigger |
|---|---|---|
| above training range | `{field} is above the training range (max {max})` | Numeric input above the training maximum |
| below training range | `{field} is below the training range (min {min})` | Numeric input below the training minimum |
| rare category | `{field} '{value}' appears fewer than 5 times in the training data and is treated as Other` | `category_status` is `rare` |
| unseen category | `{field} '{value}' was not seen in training and is treated as Other` | `category_status` is `unseen` |
| os and processor | `os is ios but processor_brand is not an Apple processor; check the inputs` | `os = ios` and `processor_brand` not in `APPLE_PROCESSOR_BRANDS` |

A warning means "the model is extrapolating or guessing a category". The UI shows warnings in a notice above the result.

## 8. Analytics schemas

### 8.1 Query parameters (**implementation choice** for the names)

| Parameter | Values | Default | Notes |
|---|---|---|---|
| `segment` | `Budget`, `Mid-range`, `Premium`; repeatable | all | Multi-select |
| `brand` | lowercase brand; repeatable; `other` | all | Top 12 by count, then `other` |
| `price_min`, `price_max` | integers in INR | data min and max | Log slider in the UI |
| `fiveg` | `any`, `yes`, `no` | `any` | |
| `include_outliers` | `0`, `1` | `0` | Value Finder only; `1` includes prices above 150,000 |

Filters are normalised (values sorted, defaults dropped, brand names lowercased) into one tuple, which is the cache key. The top 12 brands on the shipped data are xiaomi, samsung, vivo, realme, oppo, motorola, apple, oneplus, poco, tecno, iqoo and infinix.

### 8.2 Envelope

```json
{
  "view": "ram_price",
  "title": "RAM vs price",
  "chart": "box",
  "filters": { "segment": ["Budget"], "fiveg": "any" },
  "n": 412,
  "takeaway": "Median price rises with RAM across the tiers shown.",
  "caveat": "Storage and RAM are correlated.",
  "suppressed": [ { "label": "1 GB", "n": 3 } ],
  "data": { },
  "table": { "columns": ["RAM (GB)", "n", "Median price"], "rows": [[4, 120, 12999]] }
}
```

`table` carries the same numbers as `data` and feeds the `<details>` data table. `suppressed` lists groups hidden by the n-below-10 rule.

### 8.3 Per-view `data`

| View id | Title | `data` shape |
|---|---|---|
| kpi | Overview | `{phones, brands, median_price, share_5g, median_ram, share_fast_charging}` (shares are fractions 0 to 1) |
| price_dist | Price distribution | `{cutoffs: [20000, 40000], log_x: true, bins: [{low, high, count, by_segment: {Budget, Mid-range, Premium}}]}` |
| segment_mix | Segment mix by brand | `{brands: [{brand, n, share: {Budget, Mid-range, Premium}}]}`, brands with n of 10 or more |
| brand_price | Brand price ranking | `{brands: [{brand, n, median, q1, q3}]}`, sorted by median |
| ram_price | RAM vs price | `{x_label, log_y: true, groups: [{x, n, min, q1, median, q3, max, outliers: []}]}` |
| storage_price | Storage vs price | Same shape as `ram_price` |
| refresh_price | Refresh rate vs price | Same shape as `ram_price` |
| fiveg | 5G adoption | `{segments: [{segment, n, share_5g, n_5g, n_no5g, median_price_5g, median_price_no5g}]}` |
| charging | Charging by segment | `{segments: [{segment, n, min, q1, median, q3, max}], excluded: {unknown_or_none: int}}` |
| battery_scatter | Battery vs price | `{log_y: true, points: [{row_id, battery, price, segment, model}]}` |
| corr | Correlation | `{method: 'spearman', labels: [...], matrix: [[...]]}` over the 15 raw numeric features plus `log_price` |
| value | Value Finder | `{banner, include_outliers, total, flagged, rows: [{row_id, model, brand, price, predicted_price, interval_low, interval_high, score, label}]}` |
| data_notes | Data notes | `{issues: [{id, issue, evidence, handling}], caveats: [...], group_audit: {...}}` |

### 8.4 Value Finder row

| Field | Definition |
|---|---|
| `score` | `resid / q_band`, with `resid = log1p(price) − z_hat_oof` and the band from `expm1(z_hat_oof)` |
| `label` | `"Listed above spec-implied range"` if `score > 1`; `"Listed below spec-implied range"` if `score < −1`; otherwise `null` |
| `interval_low`, `interval_high` | `expm1(z_hat_oof ∓ q_band)`, the same construction as the prediction interval |
| `banner` | "Diagnostic estimates from cross-validated predictions, not a performance statistic. Model performance is reported only on the locked test set (Models page)." |

About 20% of phones are labelled by construction. Rows are sorted by `abs(score)` descending. The words "bargain" and "overpriced" never appear.

## 9. Artifact schemas

### 9.1 `artifacts/splits.json`

```json
{ "outer": { "seed": 42, "train_row_ids": [], "test_row_ids": [] },
  "cv_splits": { "seeds": [11, 22, 33], "pairs": [ { "train": [], "validation": [] } ] },
  "brand_holdout": { "n_splits": 5, "pairs": [] } }
```

All arrays hold `row_id` values, never positions. `pairs` has 15 entries in `cv_splits`.

### 9.2 `artifacts/manifest.json`

```json
{
  "schema_version": 1,
  "created_utc": "2026-09-30T10:00:00Z",
  "git_commit": null,
  "python": "3.12.3", "scikit_learn": "1.8.0", "pandas": "3.0.2", "numpy": "2.4.4", "joblib": "1.5.3",
  "data_sha256": "…",
  "seed": 42,
  "features": ["brand_name", "…"],
  "split_sizes": { "train": 784, "test": 196 },
  "cv_split_seeds": [11, 22, 33],
  "calibration_split_seed": 5,
  "selected": {
    "regression": { "name": "random_forest", "params": { } },
    "classification": { "name": "random_forest", "params": { }, "calibration": "none" }
  },
  "q_band": { "A": 0.23, "B": 0.34, "C": 0.43 },
  "q_global": 0.31,
  "calibration_decision": "none",
  "headline_metrics": { }
}
```

Fields follow `spec.md` §12.3. The version guard reads `python`, `scikit_learn`, `pandas`, `numpy` and `joblib`. `q_band` and `q_global` appear here and in the regressor bundle; a test asserts they agree.

### 9.3 Model bundles (`*.joblib`, plain dicts)

| File | Keys |
|---|---|
| `regressor.joblib` | `pipeline`, `features`, `q_band`, `q_global`, `training_median` (dict), `training_range` (dict of min and max), `name`, `version`, `trained_at` |
| `classifier.joblib` | `estimator`, `classes` (in order), `calibration` (`none` or `sigmoid_grouped`), `features`, `name`, `version` |
| `comparables.joblib` | `matrix` (N × 7 standardised), `mean`, `sd`, `columns`, `row_id`, `model_display`, `price`, `specs` (N × 23 raw) |

### 9.4 `reports/group_audit.json`

```json
{ "n_rows": 980, "base_name_groups": 785, "dup_groups": 733,
  "rows_in_multirow_base_groups": 348, "rows_in_multirow_dup_groups": 424, "largest_group": 6,
  "over_merge": { "multirow_base_groups": 153, "groups_differing_in_non_memory_spec": 3 },
  "under_merge": { "clusters_before_union": 47, "rows_before_union": 128, "clusters_after_union": 0 } }
```

### 9.5 `artifacts/metrics.json` (**implementation choice** for the exact keys)

| Block | Contents |
|---|---|
| `schema_version`, `generated_utc`, `data` | Version, time, `sha256`, `n_rows`, `n_train`, `n_test` |
| `regression.selected` | `name`, `params` |
| `regression.cv` | `n_folds` (15); per candidate: `mdape_mean`, `mdape_sd`, `r2_log_mean`, `wins_vs_ridge`, `mean_paired_gain` |
| `regression.test` | `mdape`, `r2_log`, `mae_inr`, `mae_mainstream_inr`, `by_segment` (n, mdape, mae each), `bootstrap` (`null` or ranges plus `n_resamples`) |
| `regression.brand_holdout` | `r2_log`, `mdape`, `per_brand` (brand, n, mdape) for the 17 brands with n of 10 or more |
| `regression.intervals` | `level`, `method`, `q_band`, `q_global`, `coverage.overall`, `coverage.by_band`, `coverage.by_segment` (each with `coverage` and `n`) |
| `regression.importance` | `by_group` and `by_feature` (mean, sd); `partial_dependence` is `null` when skipped |
| `classification.selected` | `name`, `params`, `calibration` |
| `classification.cv` | Per candidate: `macro_f1_mean`, `macro_f1_sd`, `accuracy_mean`; includes `majority` and `regress_then_bin` |
| `classification.test` | `accuracy`, `macro_f1`, `qwk`, `budget_premium_confusions`, `per_class` (precision, recall, f1, support), `confusion_matrix` (`labels`, `matrix`), `log_loss`, `brier` |
| `classification.calibration_comparison` | `uncalibrated` and `sigmoid_grouped` (mean log loss and Brier on `CV_SPLITS`), `decision`, `margin` |
| `classification.reliability` | Per class: bin edges, mean predicted, observed fraction, for the chosen variant and the alternative |
| `leakage_audit` | `feature_list_ok`, `group_overlap`, `label_shuffle` (regression R², classification accuracy, majority rate), `top_feature_ablation`, `triggered` |
| `gates` | `QG-01` to `QG-14`, each with `passed`, measured `value` and `threshold` |

`interval.observed_coverage` in the API is read from `regression.intervals.coverage`.

### 9.6 `artifacts/analytics.json`

```json
{ "schema_version": 1, "q_band": { "A": 0.23, "B": 0.34, "C": 0.43 }, "q_global": 0.31,
  "rows": [ { "row_id": 0, "z_hat_oof": 9.87, "band": "B", "resid": 0.12, "score": 0.35 } ] }
```

Display fields (model name, listed price, brand) are joined from the cleaned frame at request time.

### 9.7 `artifacts/model_card.md`

Sections in this order: intended use and non-use; data source, the §2.2 audit and the §3.1 group audit; features and exclusions with reasons; cross-validation and test metrics for both modules; per-segment errors; brand-held-out result; calibration decision; interval coverage with n per segment; failure modes; limitations (snapshot, INR assumption, listing prices); how to retrain.

## 10. Data contracts that must always hold

1. `row_id` is unique, runs 0 to 979 in raw-file order, and is the only row identity used in splits, groups, OOF predictions and analytics.
2. `dup_group` is the only grouping key for splits, CV and calibration folds.
3. No feature in `FEATURES` appears in `FORBIDDEN_FEATURES`.
4. The classifier and regressor use the same `FEATURES` list in the same order.
5. `fast_charging_w` is NaN exactly where `fast_charging <= 0`.
6. `q_band` is identical in the manifest, the regressor bundle and `analytics.json`.
7. The interval is `[expm1(z − q), expm1(z + q)]`, never `price × exp(±q)`.
8. Probabilities sum to 1 within floating-point tolerance.
9. Only `scripts/evaluate.py` reads test rows.