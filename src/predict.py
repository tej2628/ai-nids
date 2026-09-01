import joblib
import pandas as pd
from config import MODEL_PATH


class Predictor:
    def __init__(self, model_path=MODEL_PATH):
        if not model_path.exists(): raise FileNotFoundError("Model not trained. Run: python -m src.train_model")
        artifact = joblib.load(model_path)
        self.pipeline, self.features, self.metrics = artifact["pipeline"], artifact["features"], artifact["metrics"]

    def predict(self, record):
        frame = pd.DataFrame([record]).reindex(columns=self.features)
        label = self.pipeline.predict(frame)[0]
        probabilities = self.pipeline.predict_proba(frame)[0]
        confidence = float(max(probabilities))
        return {"prediction": label, "confidence": round(confidence, 4), "attack_type": "Suspicious Traffic" if label == "ATTACK" else "None"}
