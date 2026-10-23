from pathlib import Path

import pytest

ART = Path(__file__).resolve().parents[1] / "ml" / "artifacts" / "cnn_model.keras"


@pytest.mark.skipif(not ART.exists(), reason="CNN not trained")
def test_cnn_predict():
    from ml.predict import predict_cnn

    r = predict_cnn("Free diamonds click http://evil.xyz now")
    assert r.label in (0, 1)
    assert 0 <= r.phishing_probability <= 1
