# Backend — Phishing Detection API

FastAPI service and ML training code. See the root [README.md](../README.md) for full setup.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

## ML workflow

1. `python ml\data\generate_synthetic.py` — dev dataset only  
2. `python ml\data\prepare_dataset.py` — train/val/test CSVs  
3. `python ml\train_cnn.py` / `train_bilstm.py` / `train_tinybert.py`  
4. `python ml\evaluate.py` — writes `ml/artifacts/evaluation_results.json`

## Environment variables (optional `.env`)

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `DEFAULT_MODEL` | `baseline` | `cnn`, `bilstm`, `tinybert`, or `baseline` |
| `MAX_MESSAGE_LENGTH` | `5000` | Input cap for `/analyze` |
