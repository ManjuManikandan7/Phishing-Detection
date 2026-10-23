import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Loader2,
  Shield,
  ShieldAlert,
  Trash2,
  Wand2,
} from "lucide-react";
import { analyzeMessage, fetchEvaluation, fetchHealth, fetchModels } from "./api";

const SAMPLE_PHISHING =
  "URGENT! You won 5000 FREE DIAMONDS in Mobile Legends! Claim now at http://ml-diamonds-free.xyz/login and verify your password within 30 minutes or your account will be locked.";

const SAMPLE_LEGIT =
  "Hey, ranked queue tonight at 8pm? I'll be online after dinner. We can push for diamond if everyone's free.";

function riskColor(score) {
  if (score <= 30) return "var(--risk-low)";
  if (score <= 60) return "var(--risk-suspicious)";
  if (score <= 80) return "var(--risk-high)";
  return "var(--risk-critical)";
}

function classificationIcon(name) {
  if (name === "Phishing") return ShieldAlert;
  if (name === "Suspicious") return AlertTriangle;
  return CheckCircle2;
}

export default function App() {
  const [message, setMessage] = useState("");
  const [selectedModel, setSelectedModel] = useState("baseline");
  const [models, setModels] = useState([]);
  const [defaultModel, setDefaultModel] = useState("baseline");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiOnline, setApiOnline] = useState(null);
  const [evaluation, setEvaluation] = useState(null);

  const loadMeta = useCallback(async () => {
    try {
      await fetchHealth();
      setApiOnline(true);
      const m = await fetchModels();
      setModels(m.models || []);
      setDefaultModel(m.default_model || "baseline");
      setSelectedModel((prev) => prev || m.default_model);
      const ev = await fetchEvaluation();
      setEvaluation(ev);
    } catch {
      setApiOnline(false);
    }
  }, []);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  const onAnalyze = async () => {
    setError("");
    setResult(null);
    if (!message.trim()) {
      setError("Please enter a message to analyze.");
      return;
    }
    setLoading(true);
    try {
      const data = await analyzeMessage(message, selectedModel);
      setResult(data);
    } catch (e) {
      setError(e.message || "Could not reach the API. Start the backend with uvicorn.");
    } finally {
      setLoading(false);
    }
  };

  const bestModelNote = useMemo(() => {
    if (!evaluation?.available || !evaluation.best_by_f1) return null;
    return `Highest F1 on held-out test (when evaluation was run): ${evaluation.best_by_f1}`;
  }, [evaluation]);

  const ResultIcon = result ? classificationIcon(result.classification) : Shield;

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <Shield className="brand-icon" aria-hidden />
          <div>
            <h1>Phishing Detection</h1>
            <p>CNN · Bi-LSTM · TinyBERT · Text analysis dashboard</p>
          </div>
        </div>
        <div className={`api-pill ${apiOnline === false ? "offline" : apiOnline ? "online" : ""}`}>
          {apiOnline === false ? "API offline" : apiOnline ? "API connected" : "Checking API…"}
        </div>
      </header>

      <main className="layout">
        <section className="card input-card">
          <h2>Analyze a message</h2>
          <p className="muted">
            Paste SMS, chat, or in-game text. This tool analyzes text you submit — it does not read game chats
            automatically.
          </p>

          <label className="field-label" htmlFor="model-select">
            Model
          </label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="select"
          >
            {(models.length ? models : [{ id: "baseline", name: "Rule-Based Baseline", status: "available" }]).map(
              (m) => (
                <option key={m.id} value={m.id} disabled={m.status === "not_trained"}>
                  {m.name} {m.status === "not_trained" ? "(not trained)" : m.status === "available" ? "" : ""}
                </option>
              ),
            )}
          </select>
          {selectedModel === "baseline" && (
            <p className="baseline-note">Using explicit rule-based baseline — not a trained deep learning model.</p>
          )}

          <textarea
            id="message-input"
            className="textarea"
            rows={8}
            placeholder="Paste message here…"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={5000}
          />

          <div className="actions">
            <button type="button" className="btn primary" onClick={onAnalyze} disabled={loading}>
              {loading ? <Loader2 className="spin" size={18} /> : <Wand2 size={18} />}
              Analyze Message
            </button>
            <button type="button" className="btn ghost" onClick={() => { setMessage(""); setResult(null); setError(""); }}>
              <Trash2 size={18} /> Clear
            </button>
            <button type="button" className="btn ghost" onClick={() => setMessage(SAMPLE_PHISHING)}>
              Sample phishing
            </button>
            <button type="button" className="btn ghost" onClick={() => setMessage(SAMPLE_LEGIT)}>
              Sample legitimate
            </button>
          </div>

          {error && (
            <div className="alert error" role="alert">
              <AlertTriangle size={18} /> {error}
            </div>
          )}
        </section>

        <section className="card result-card">
          <h2>Results</h2>
          {!result && !loading && <p className="muted">Run analysis to see risk score and warning signs.</p>}
          {loading && (
            <div className="loading-block">
              <Loader2 className="spin large" />
              <span>Analyzing…</span>
            </div>
          )}
          {result && (
            <>
              <div className="result-header">
                <ResultIcon size={28} style={{ color: riskColor(result.risk_score) }} />
                <div>
                  <div className="classification">{result.classification}</div>
                  <div className="muted small">Model: {result.model_used}</div>
                </div>
              </div>

              <div className="score-ring" style={{ "--score-color": riskColor(result.risk_score) }}>
                <div className="score-value">{result.risk_score}</div>
                <div className="score-label">Risk score (0–100)</div>
                <div className="score-band">{result.risk_band}</div>
              </div>

              <p className="note">{result.confidence_note}</p>
              <p className="recommended">
                <strong>Recommended action:</strong> {result.recommended_action}
              </p>

              {result.warning_signs?.length > 0 ? (
                <ul className="signs">
                  {result.warning_signs.map((s, i) => (
                    <li key={i} className={`sign ${s.severity}`}>
                      <span className="sign-cat">{s.category}</span>
                      {s.description}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No rule-based warning signs flagged.</p>
              )}
            </>
          )}
        </section>

        <section className="card eval-card">
          <h2>
            <BarChart3 size={20} /> Model comparison
          </h2>
          {!evaluation?.available && (
            <p className="muted">
              No evaluation results yet. Train models and run{" "}
              <code className="inline-code">python ml/evaluate.py</code> in the backend folder.
            </p>
          )}
          {evaluation?.available && (
            <>
              <p className="muted small">{evaluation.dataset_note}</p>
              {bestModelNote && <p className="best-note">{bestModelNote}</p>}
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Accuracy</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1</th>
                      <th>ROC-AUC</th>
                      <th>ms/msg</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evaluation.results.map((row) => (
                      <tr key={row.model_id} className={row.model_id === evaluation.best_by_f1 ? "best-row" : ""}>
                        <td>{row.model_id}</td>
                        <td>{row.accuracy?.toFixed(3) ?? "—"}</td>
                        <td>{row.precision?.toFixed(3) ?? "—"}</td>
                        <td>{row.recall?.toFixed(3) ?? "—"}</td>
                        <td>{row.f1_score?.toFixed(3) ?? "—"}</td>
                        <td>{row.roc_auc != null ? row.roc_auc.toFixed(3) : "—"}</td>
                        <td>{row.avg_inference_ms?.toFixed(1) ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="bars">
                {evaluation.results.map((row) => (
                  <div key={row.model_id} className="bar-row">
                    <span>{row.model_id}</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${(row.f1_score || 0) * 100}%` }} />
                    </div>
                    <span className="bar-val">F1 {(row.f1_score || 0).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>
          Default API model: {defaultModel}. Risk bands (0–30 / 31–60 / 61–80 / 81–100) are initial settings — validate
          on your dataset.
        </p>
      </footer>
    </div>
  );
}
