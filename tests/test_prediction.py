from pathlib import Path
from src.train_model import train
from src.predict import Predictor

def test_training_and_prediction(tmp_path):
    source=Path(__file__).parents[1]/'data'/'raw'/'synthetic_demo.csv'
    model=tmp_path/'model.joblib'; metrics=tmp_path/'metrics.json'
    result=train(source,model,metrics)
    assert 0 <= result['f1'] <= 1
    prediction=Predictor(model).predict({"source_ip":"1.2.3.4","destination_ip":"10.0.0.10","protocol":"TCP","source_port":5000,"destination_port":443,"flow_duration":10,"total_packets":20,"total_bytes":10000,"packet_rate":2,"service":"https"})
    assert prediction['prediction'] in ('NORMAL','ATTACK')
