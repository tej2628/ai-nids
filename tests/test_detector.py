from src.database import init_database, get_recent_detections
from src.detector import Detector, risk_level

class FakePredictor:
    def predict(self, flow): return {"prediction":"ATTACK","confidence":.91,"attack_type":"Test Attack"}

def test_detector_inserts_event(tmp_path):
    db=tmp_path/'events.db'; init_database(db)
    event=Detector(FakePredictor(),db).analyse({"source_ip":"1.1.1.1","destination_ip":"2.2.2.2","protocol":"TCP"},"TEST")
    assert event['risk_level']=='CRITICAL'; assert len(get_recent_detections(db_path=db))==1
def test_risk_normal(): assert risk_level('NORMAL',.99)=='LOW'
