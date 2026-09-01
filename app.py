from flask import Flask, jsonify, render_template, request
from config import SECRET_KEY, HOST, PORT, MODEL_PATH, METRICS_PATH, RAW_DATA_DIR
from src.database import init_database, get_stats, get_recent_detections
from src.detector import Detector
from src.demo import DemoRunner
from src.packet_capture import PacketMonitor
from src.train_model import train
from src.utils import logger
import json

app = Flask(__name__); app.config.update(SECRET_KEY=SECRET_KEY, MAX_CONTENT_LENGTH=20*1024*1024)
init_database(); detector = None; demo = None; monitor = None

def services():
    global detector, demo, monitor
    if detector is None:
        detector=Detector(); demo=DemoRunner(detector); monitor=PacketMonitor(detector)
    return demo, monitor

def model_info():
    if not METRICS_PATH.exists(): return {"trained":False,"message":"No trained model. Train the bundled synthetic dataset or add a CSV."}
    try: return {"trained":True, **json.loads(METRICS_PATH.read_text(encoding="utf-8"))}
    except (OSError, json.JSONDecodeError): return {"trained":False,"message":"Model metrics could not be read."}

@app.get("/")
def index(): return render_template("index.html")
@app.get("/detections")
def detections(): return render_template("detections.html")
@app.get("/traffic")
def traffic(): return render_template("traffic.html")
@app.get("/model")
def model(): return render_template("model.html")
@app.get("/about")
def about(): return render_template("about.html")

@app.get("/api/stats")
def api_stats():
    stats=get_stats(); stats["mode"]="DEMO" if demo and demo.running else "LIVE" if monitor and monitor.running else "OFFLINE"; return jsonify(stats)
@app.get("/api/detections")
def api_detections(): return jsonify(get_recent_detections(request.args.get("limit",50), request.args.get("search","")[:100], request.args.get("prediction", "")))
@app.get("/api/model")
def api_model(): return jsonify(model_info())
@app.post("/api/train")
def api_train():
    path=RAW_DATA_DIR / request.json.get("filename","synthetic_demo.csv") if request.is_json else RAW_DATA_DIR / "synthetic_demo.csv"
    try: return jsonify(train(path))
    except Exception as exc: logger.exception("Training failed"); return jsonify(error=str(exc)), 400
@app.post("/api/start-demo")
def start_demo():
    try: d,m=services(); m.stop(); d.start(); return jsonify(message="Demo mode started",mode="DEMO")
    except Exception as exc: return jsonify(error=str(exc)),400
@app.post("/api/stop-demo")
def stop_demo():
    if demo: demo.stop()
    return jsonify(message="Demo mode stopped")
@app.post("/api/start-monitoring")
def start_monitoring():
    try: d,m=services(); d.stop(); m.start(); return jsonify(message="Live monitoring started",mode="LIVE")
    except Exception as exc: return jsonify(error=f"Live monitoring unavailable: {exc}"),400
@app.post("/api/stop-monitoring")
def stop_monitoring():
    if monitor: monitor.stop()
    return jsonify(message="Live monitoring stopped")
@app.errorhandler(413)
def too_large(_): return jsonify(error="Request too large"),413

if __name__ == "__main__":
    logger.info("AI-NIDS starting"); app.run(host=HOST, port=PORT, debug=False)
