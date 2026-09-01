from src.database import init_database, insert_detection, get_recent_detections, get_stats

def test_database_roundtrip(tmp_path):
    db=tmp_path/'test.db'; init_database(db)
    insert_detection({"source_ip":"1.1.1.1","destination_ip":"2.2.2.2","protocol":"TCP","source_port":1,"destination_port":2,"prediction":"ATTACK","attack_type":"Test","confidence":.9,"risk_level":"HIGH","mode":"TEST"},db)
    assert get_recent_detections(db_path=db)[0]['source_ip']=='1.1.1.1'
    assert get_stats(db)['attacks']==1
