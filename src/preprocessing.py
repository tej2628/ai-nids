from pathlib import Path
import pandas as pd

LABEL_CANDIDATES = ("label", "Label", "class", "Class", "attack_cat", "Attack", "attack", "target")


def find_label_column(frame: pd.DataFrame) -> str:
    normalized = {str(c).strip().lower(): c for c in frame.columns}
    for candidate in LABEL_CANDIDATES:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    raise ValueError("No label column found. Use one of: " + ", ".join(LABEL_CANDIDATES))


def load_dataset(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file(): raise FileNotFoundError(f"Dataset not found: {path}")
    frame = pd.read_csv(path, low_memory=False)
    if frame.empty: raise ValueError("Dataset CSV is empty")
    label = find_label_column(frame)
    frame = frame.rename(columns={label: "label"})
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame


def normalise_labels(labels: pd.Series) -> pd.Series:
    text = labels.fillna("unknown").astype(str).str.strip()
    normal = text.str.lower().isin({"normal", "benign", "0", "no", "non-attack"})
    return text.where(~normal, "NORMAL")


def clean_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    if "label" not in frame: raise ValueError("Internal label column is required")
    clean = frame.copy().replace([float("inf"), float("-inf")], pd.NA).drop_duplicates()
    clean["label"] = normalise_labels(clean["label"])
    clean = clean.dropna(subset=["label"])
    if clean["label"].nunique() < 2: raise ValueError("Dataset needs at least two label classes")
    return clean
