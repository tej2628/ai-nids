# AI-Based Network Intrusion Detection System (AI-NIDS)

AI-NIDS is an offline-first, defensive Flask project that trains a Random Forest classifier on network-flow CSV data, records predictions in SQLite, and presents them in a web dashboard. It includes safe **SYNTHETIC DEMONSTRATION DATA** and optional authorized Scapy packet capture.

## Architecture
Dataset/live packet -> flow features -> preprocessing pipeline -> Random Forest -> prediction/confidence -> SQLite -> Flask dashboard. The saved joblib artifact contains the preprocessing and model together, preventing train/predict transformation drift.

## Installation and running (Windows 10/11)
Use Python 3.11+.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.train_model
python app.py
```

For CMD activation use `venv\Scripts\activate.bat`. Open `http://127.0.0.1:5000`.

Run tests with `pytest`.

## Dataset and training
Place CSV files in `data/raw/`, then run `python -m src.train_model data/raw/your_file.csv`. Supported common label names include `Label`, `label`, `Class`, `class`, and `attack_cat`. Categorical columns use one-hot encoding; numerical missing values use median imputation; infinite values become missing; duplicate rows are removed. Labels including BENIGN and NORMAL become NORMAL; all other labels are consolidated to ATTACK for the baseline detector. The train/test split is stratified and all transformations are fit only on training data. Random Forest class weights address imbalance; the saved metrics report class distribution.

CICIDS2017, UNSW-NB15 and NSL-KDD CSV exports may be used when they include a label column and flow-like fields. Dataset-specific cleanup may be necessary for source-specific files.

## Modes
Use **Start Demo** for safe generated flow records; it never creates traffic or performs attacks. Live monitoring is opt-in only. Install Npcap in WinPcap-compatible mode, run an elevated terminal if required, select a valid adapter, and click **Start Monitoring**. If capture fails, the application remains usable in offline/demo mode.

## Limitations
This is a project baseline, not an IPS or professional SOC product. Model confidence is a model score, not a verified probability of malicious activity. Packet-level live capture uses minimal flow features and should be validated against authorized local traffic before any deployment.

## Troubleshooting
`Model not trained`: run `python -m src.train_model`. `Live monitoring unavailable`: install Npcap, verify permission/interface configuration, or use Demo Mode. `No label column`: rename/add an accepted label column. Logs are written to `logs/app.log`.
