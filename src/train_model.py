import argparse, json, time
from pathlib import Path
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from config import MODEL_PATH, METRICS_PATH, RAW_DATA_DIR
from src.preprocessing import load_dataset, clean_dataset
from src.utils import logger


def train(dataset_path, model_path=MODEL_PATH, metrics_path=METRICS_PATH):
    started = time.perf_counter()
    data = clean_dataset(load_dataset(dataset_path))
    y = data.pop("label").apply(lambda x: "NORMAL" if x == "NORMAL" else "ATTACK")
    X = data.dropna(axis=1, how="all")
    numeric = X.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    if not numeric and not categorical: raise ValueError("Dataset has no usable feature columns")
    transformer = ColumnTransformer([
        ("num", Pipeline([( "impute", SimpleImputer(strategy="median"))]), numeric),
        ("cat", Pipeline([( "impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    pipeline = Pipeline([( "preprocess", transformer), ("model", RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced", n_jobs=-1))])
    pipeline.fit(X_train, y_train)
    prediction = pipeline.predict(X_test)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, prediction, average="weighted", zero_division=0)
    metrics = {"model_name":"Random Forest", "accuracy":round(accuracy_score(y_test,prediction),4), "precision":round(precision,4), "recall":round(recall,4), "f1":round(f1,4), "confusion_matrix":confusion_matrix(y_test,prediction,labels=["NORMAL","ATTACK"]).tolist(), "classes":["NORMAL","ATTACK"], "classification_report":classification_report(y_test,prediction,zero_division=0), "training_samples":len(X_train), "testing_samples":len(X_test), "feature_count":len(X.columns), "training_seconds":round(time.perf_counter()-started,2), "dataset":str(Path(dataset_path).name), "class_distribution":y.value_counts().to_dict()}
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline":pipeline,"features":X.columns.tolist(),"metrics":metrics}, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info("Trained model with %s samples from %s", len(data), dataset_path)
    return metrics


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Train AI-NIDS model")
    parser.add_argument("dataset", nargs="?", default=str(RAW_DATA_DIR / "synthetic_demo.csv"))
    print(json.dumps(train(parser.parse_args().dataset), indent=2))
