# Phishing Detection Using CNN, Bi-LSTM & TinyBERT

Full-stack M.Sc.-style project: React dashboard + FastAPI backend + three text classifiers and an explicit rule-based baseline.

## Requirements

| Component | Version |
| --------- | ------- |
| Python    | 3.10+ recommended |
| Node.js   | 18+ |
| OS        | Windows / Linux / macOS |

## Project structure

```
phishing_detection/
├── backend/          # FastAPI + ML training & inference
│   ├── main.py
│   ├── ml/
│   └── tests/
└── frontend/         # Vite + React dashboard
```

## 1. Backend setup (PowerShell)

```powershell
cd phishing_detection\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Dataset (development)

Synthetic labeled data for smoke testing lives in `ml/data/messages_labeled.csv`. Regenerate with:

```powershell
python ml\data\generate_synthetic.py
python ml\data\prepare_dataset.py
```

See `ml/data/DATASETS.md` for label mapping and notes on replacing synthetic data with licensed public datasets.

### Train models

```powershell
python ml\train_cnn.py
python ml\train_bilstm.py
python ml\train_tinybert.py   # downloads TinyBERT from Hugging Face; needs network
```

TinyBERT training requires internet access on first run. If training has not completed, the API returns **503** for that model (no silent fallback).

### Evaluate (same test split for all models)

```powershell
python ml\evaluate.py
```

Results are written to `ml/artifacts/evaluation_results.json` and exposed at `GET /evaluation`.

### Run API

```powershell
uvicorn main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs  
- Default model: `baseline` (set `DEFAULT_MODEL=cnn|bilstm|tinybert` in `.env` after training)

### Tests

```powershell
pytest tests -q
```

## 2. Frontend setup (second terminal)

```powershell
cd phishing_detection\frontend
npm install
npm run dev
```

Open http://localhost:5173

Optional: `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env`

## API endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/` | App info |
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze message JSON `{ "message": "...", "model": "baseline" }` |
| GET | `/models` | Model availability |
| GET | `/evaluation` | Test metrics if `evaluate.py` was run |

## Risk score

- Score = model phishing-class output × 100 (sigmoid/softmax). Documented as **not** a calibrated real-world probability unless you add calibration.
- Display bands: 0–30 Low, 31–60 Suspicious, 61–80 High, 81–100 Critical (initial thresholds).

## Security notes

- Message text is processed in memory for analysis only (not persisted by default).
- Max message length: 5000 characters.
- Suspicious URLs are **not** fetched by the server.
- CORS is limited to local Vite dev origins.

## Troubleshooting

| Issue | Fix |
| ----- | --- |
| `503` for CNN/Bi-LSTM/TinyBERT | Train that model; artifacts must exist under `ml/artifacts/` |
| TinyBERT download fails | Check VPN/firewall; set `HF_HOME` if needed |
| Frontend "API offline" | Start uvicorn; confirm port 8000 |
| TensorFlow install errors | Use Python 3.10–3.11; see tensorflow.org install matrix |
| pytest import errors | Run from `backend` with venv activated |

## What is real vs demo

| Feature | Status |
| ------- | ------ |
| Rule-based baseline | Works without training |
| CNN / Bi-LSTM / TinyBERT | Requires training scripts |
| Evaluation table in UI | Only after `ml/evaluate.py` |
| Synthetic dataset metrics | **Not** real-world performance |

## License

Academic project template — add your institution’s requirements and dataset licenses when you extend the data.
