import numpy as np
import pandas as pd
from anomaly_detection import detect_anomalies

def test_zscore_finds_extreme_point():
    values = np.r_[np.ones(100) * 10, 100]
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=len(values), freq="5min"),
        "value": values,
    })
    out = detect_anomalies(df, "Z-score")
    assert bool(out.iloc[-1]["is_anomaly"])

def test_empty_input():
    out = detect_anomalies(pd.DataFrame(columns=["timestamp","value"]), "Combined")
    assert out.empty
