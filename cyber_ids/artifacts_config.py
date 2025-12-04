from pathlib import Path

# Base directory of the Django project (folder containing manage.py)
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Directory containing this config file (cyber_ids app folder)
APP_DIR: Path = Path(__file__).resolve().parent

# Root folder where notebook saved all artifacts (inside the cyber_ids app)
ARTIFACTS_ROOT: Path = APP_DIR / "artifacts"

# Subfolders for different artifact types
MODELS_DIR: Path = ARTIFACTS_ROOT / "models"
META_DIR: Path = ARTIFACTS_ROOT / "meta"

# File naming basenames (must match the notebook cell that saves artifacts)
MODEL_BASENAME = "cyber_ids_champion"
FEATURES_BASENAME = "cyber_ids_features"
METADATA_BASENAME = "cyber_ids_metadata"
SANITIZER_BASENAME = "cyber_ids_sanitizer"

# Suffixes
MODEL_SUFFIX = ".joblib"
META_SUFFIX = ".json"
SANITIZER_SUFFIX = ".joblib"

# Default threshold for converting probabilities to labels
DEFAULT_DECISION_THRESHOLD: float = 0.5
