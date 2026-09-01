from src.database import insert_detection
from src.predict import Predictor


def risk_level(prediction, confidence):
    if prediction == "NORMAL": return "LOW"
    if confidence >= .90: return "CRITICAL"
    if confidence >= .75: return "HIGH"
    return "MEDIUM"


class Detector:
    def __init__(self, predictor=None, db_path=None):
        self.predictor = predictor or Predictor()
        self.db_path = db_path

    def analyse(self, flow, mode="OFFLINE"):
        outcome = self.predictor.predict(flow)
        event = {"source_ip": str(flow.get("source_ip", "0.0.0.0")), "destination_ip": str(flow.get("destination_ip", "0.0.0.0")), "protocol": str(flow.get("protocol", "UNKNOWN")), "source_port": int(flow.get("source_port", 0) or 0), "destination_port": int(flow.get("destination_port", 0) or 0), "mode": mode, **outcome}
        event["risk_level"] = risk_level(event["prediction"], event["confidence"])
        event["id"] = insert_detection(event, self.db_path) if self.db_path else insert_detection(event)
        return event
