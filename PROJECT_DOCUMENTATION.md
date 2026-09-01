# AI-NIDS Project Documentation

## Abstract and introduction
AI-NIDS applies supervised machine learning to labelled network-flow data to support defensive traffic triage. It offers offline analysis, safe simulation, optional authorized live capture, persistent event storage, and a web UI.

## Problem, existing and proposed systems
Manual log review is slow and signature-only systems can miss novel patterns. The proposed system learns normal-versus-attack distinctions from labelled data, records results, and makes trends visible. It is an IDS: it reports; it does not block traffic (an IPS blocks).

## Objectives and scope
Objectives are dataset validation, leak-resistant preprocessing, Random Forest training/evaluation, prediction, risk indication, SQLite audit events and demonstration UI. Scope is authorized network monitoring; it is not a production replacement for a SOC.

## Requirements
Windows 10/11, Python 3.11+, 4 GB RAM recommended; Flask, pandas, NumPy, scikit-learn, joblib, pytest, and optional Scapy/Npcap.

## Architecture and modules
`preprocessing` detects labels and cleans data. `train_model` fits preprocessing only on train data and persists the pipeline. `predict` loads it. `detector` assigns risk and writes database events. `packet_capture` is opt-in. `demo` creates safe records. Flask supplies UI/API and `database` uses parameterized SQLite queries.

## Dataset, methodology and algorithms
CSV labels such as Label/Class/attack_cat are mapped to `label`; BENIGN/NORMAL become NORMAL and other types form ATTACK. Duplicates are removed; infinity becomes missing; numeric values use median imputation and categorical values use most-frequent imputation plus one-hot encoding. A stratified 75/25 split, class-weighted Random Forest, accuracy, weighted precision/recall/F1, classification report and confusion matrix are used. Actual metrics are saved after training rather than assumed.

## Detection, database and UI
Prediction returns a class and maximum model score. ATTACK risk is MEDIUM/HIGH/CRITICAL based on score; NORMAL is LOW. `detections` stores time, endpoints, protocol, ports, prediction, type, confidence, risk and mode with timestamp/prediction indexes. Dashboard, event, traffic and model pages expose the results.

## Testing and results
Pytest covers preprocessing, database insertion/retrieval, detector behavior, pipeline training and prediction. Run `pytest`; generated `models/metrics.json` provides actual project results for a report.

## Advantages, limitations, future scope and conclusion
Advantages include repeatable offline operation, transparent saved metrics, no hard-coded credentials and optional capture. Limitations include synthetic data quality, binary baseline labels and minimal live-flow aggregation. Future work: calibrated multi-class models, authenticated roles, packet aggregation, drift monitoring and SIEM integration. AI-NIDS demonstrates a safe end-to-end IDS workflow.

## References
Scikit-learn documentation; Flask documentation; Scapy documentation; CICIDS2017, UNSW-NB15 and NSL-KDD dataset documentation.
