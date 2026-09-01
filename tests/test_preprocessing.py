import pandas as pd
import pytest
from src.preprocessing import find_label_column, clean_dataset

def test_label_detection_and_cleaning():
    frame=pd.DataFrame({"Label":["BENIGN","DDoS"],"bytes":[1,float('inf')]})
    assert find_label_column(frame)=="Label"
    cleaned=clean_dataset(frame.rename(columns={"Label":"label"}))
    assert cleaned.label.tolist()==["NORMAL","DDoS"]
def test_missing_label_raises():
    with pytest.raises(ValueError): find_label_column(pd.DataFrame({"a":[1]}))
