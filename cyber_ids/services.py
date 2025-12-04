from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .artifacts_config import (
    MODELS_DIR,
    META_DIR,
    MODEL_BASENAME,
    FEATURES_BASENAME,
    METADATA_BASENAME,
    SANITIZER_BASENAME,
    MODEL_SUFFIX,
    META_SUFFIX,
    SANITIZER_SUFFIX,
    DEFAULT_DECISION_THRESHOLD,
)


@dataclass
class ArtifactBundle:
    """Container for all runtime artifacts needed by the Cyber IDS API."""

    version: str
    model: Any
    feature_names: List[str]
    metadata: Dict[str, Any]
    sanitizer: Dict[str, Any]


# Simple in-process cache so we don't hit disk on every request
_ARTIFACT_CACHE: Optional[ArtifactBundle] = None


def _discover_latest_version(meta_dir: Path = META_DIR) -> str:
    """Return the latest model version string based on metadata filenames."""
    pattern = f"{METADATA_BASENAME}_*{META_SUFFIX}"
    candidates = sorted(meta_dir.glob(pattern))
    if not candidates:
        raise FileNotFoundError(
            f"No metadata files found in {meta_dir!s} with pattern {pattern!r}."
        )
    latest = candidates[-1]
    name = latest.stem  # e.g. "cyber_ids_metadata_20251130-123456"
    prefix = f"{METADATA_BASENAME}_"
    if not name.startswith(prefix):
        raise ValueError(
            f"Unexpected metadata filename {latest.name!r}; expected it to start with {prefix!r}."
        )
    return name[len(prefix):]


def load_artifacts(version: Optional[str] = None,
                   use_cache: bool = True) -> ArtifactBundle:
    """Load the trained Cyber IDS artifacts from disk."""
    global _ARTIFACT_CACHE

    if use_cache and _ARTIFACT_CACHE is not None and version is None:
        return _ARTIFACT_CACHE

    if version is None:
        version = _discover_latest_version()

    model_path = MODELS_DIR / f"{MODEL_BASENAME}_{version}{MODEL_SUFFIX}"
    feature_list_path = META_DIR / f"{FEATURES_BASENAME}_{version}{META_SUFFIX}"
    metadata_path = META_DIR / f"{METADATA_BASENAME}_{version}{META_SUFFIX}"
    sanitizer_path = META_DIR / f"{SANITIZER_BASENAME}_{version}{SANITIZER_SUFFIX}"

    for p in (model_path, feature_list_path, metadata_path, sanitizer_path):
        if not p.exists():
            raise FileNotFoundError(f"Expected artifact not found: {p!s}")

    model = joblib.load(model_path)

    with open(feature_list_path, "r") as f:
        feature_payload = json.load(f)
    feature_names: List[str] = feature_payload.get("features", [])

    with open(metadata_path, "r") as f:
        metadata: Dict[str, Any] = json.load(f)

    sanitizer: Dict[str, Any] = joblib.load(sanitizer_path)

    bundle = ArtifactBundle(
        version=version,
        model=model,
        feature_names=feature_names,
        metadata=metadata,
        sanitizer=sanitizer,
    )

    if use_cache and version is not None:
        _ARTIFACT_CACHE = bundle

    return bundle


def apply_sanitizer(
    X: pd.DataFrame,
    sanitizer: Dict[str, Any],
    name: str = "X_request",
) -> pd.DataFrame:
    """Apply the training-time sanitizer to new data."""
    columns = sanitizer["columns"]
    medians = np.array(sanitizer["medians"], dtype="float64")

    X_num = X.reindex(columns=columns).astype("float64", copy=False)

    arr = X_num.to_numpy()
    non_finite_mask = ~np.isfinite(arr)
    if non_finite_mask.any():
        print(f"[WARN] {name}: found {non_finite_mask.sum()} non-finite values; converting to NaN.")
        arr[non_finite_mask] = np.nan

    nan_mask = np.isnan(arr)
    if nan_mask.any():
        print(f"[INFO] {name}: imputing {nan_mask.sum()} NaNs with training medians.")
        inds = np.where(nan_mask)
        arr[inds] = medians[inds[1]]

    arr = arr.astype("float32")
    return pd.DataFrame(arr, columns=columns, index=X.index)


def predict_from_dataframe(
    df: pd.DataFrame,
    threshold: float = DEFAULT_DECISION_THRESHOLD,
    artifacts: Optional[ArtifactBundle] = None,
    name: str = "X_request",
) -> Tuple[np.ndarray, np.ndarray, ArtifactBundle]:
    """Run the Cyber IDS model on a feature DataFrame."""
    if artifacts is None:
        artifacts = load_artifacts()

    feature_names = artifacts.feature_names
    sanitizer = artifacts.sanitizer
    model = artifacts.model

    df = df.reindex(columns=feature_names)

    X_clean = apply_sanitizer(df, sanitizer, name=name)

    proba = model.predict_proba(X_clean)[:, 1]
    labels = (proba >= threshold).astype(int)

    return proba, labels, artifacts
