from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
MODELS_DIR = BASE_DIR / "models"
DATABASE_PATH = BASE_DIR / "database" / "nids.db"
LOG_PATH = BASE_DIR / "logs" / "app.log"
MODEL_PATH = MODELS_DIR / "nids_pipeline.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"
SECRET_KEY = os.environ.get("AI_NIDS_SECRET_KEY", "development-only-change-me")
MAX_DETECTIONS = 250
HOST = os.environ.get("AI_NIDS_HOST", "127.0.0.1")
PORT = int(os.environ.get("AI_NIDS_PORT", "5000"))

for directory in (RAW_DATA_DIR, MODELS_DIR, DATABASE_PATH.parent, LOG_PATH.parent):
    directory.mkdir(parents=True, exist_ok=True)
