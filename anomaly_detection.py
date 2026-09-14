"""Statistical anomaly detection for refinery time-series data."""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from config import (
    ZSCORE_THRESHOLD, ROLLING_WINDOW, ROLLING_THRESHOLD,
    ISOLATION_FOREST_CONTAMINATION, MAX_IFOREST_SAMPLES, STUCK_WINDOW,
    STUCK_STD_THRESHOLD,
)

def add_zscore_flags(df: pd.DataFrame, value_col="value") -> pd.DataFrame:
    out = df.copy()
    mean = out[value_col].mean()
    std = out[value_col].std(ddof=0)
    if std == 0 or np.isnan(std):
        out["z_score"] = 0.0
        out["z_anomaly"] = False
    else:
        out["z_score"] = (out[value_col] - mean) / std
        out["z_anomaly"] = out["z_score"].abs() > ZSCORE_THRESHOLD
    return out

def add_rolling_flags(df: pd.DataFrame, value_col="value") -> pd.DataFrame:
    out = df.copy().sort_values("timestamp")
    rolling_mean = out[value_col].rolling(ROLLING_WINDOW, min_periods=ROLLING_WINDOW).mean()
    rolling_std = out[value_col].rolling(ROLLING_WINDOW, min_periods=ROLLING_WINDOW).std(ddof=0)
    out["rolling_mean"] = rolling_mean
    out["rolling_std"] = rolling_std
    upper = rolling_mean + ROLLING_THRESHOLD * rolling_std
    lower = rolling_mean - ROLLING_THRESHOLD * rolling_std
    out["rolling_anomaly"] = ((out[value_col] > upper) | (out[value_col] < lower)).fillna(False)
    out["stuck_anomaly"] = (
        out[value_col].rolling(STUCK_WINDOW, min_periods=STUCK_WINDOW)
        .std(ddof=0).fillna(np.inf) <= STUCK_STD_THRESHOLD
    )
    return out

def add_isolation_forest_flag(df: pd.DataFrame, value_col="value") -> pd.DataFrame:
    out = df.copy()
    out["iforest_anomaly"] = False
    out["iforest_score"] = 0.0
    if len(out) < 20:
        return out
    x = out[[value_col]].astype(float).values
    model = IsolationForest(
        contamination=ISOLATION_FOREST_CONTAMINATION,
        random_state=42,
        n_estimators=100,
    )
    if len(out) > MAX_IFOREST_SAMPLES:
        idx = np.linspace(0, len(out) - 1, MAX_IFOREST_SAMPLES).astype(int)
        model.fit(x[idx])
        pred = model.predict(x)
        score = -model.decision_function(x)
    else:
        model.fit(x)
        pred = model.predict(x)
        score = -model.decision_function(x)
    out["iforest_anomaly"] = pred == -1
    out["iforest_score"] = score
    return out

def detect_anomalies(df: pd.DataFrame, method="Combined") -> pd.DataFrame:
    """Return input rows with anomaly features and a final anomaly flag."""
    if df.empty:
        return df.copy()
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    out = add_zscore_flags(out)
    out = add_rolling_flags(out)
    if method in ("Isolation Forest", "Combined"):
        out = add_isolation_forest_flag(out)
    else:
        out["iforest_anomaly"] = False
        out["iforest_score"] = 0.0

    if method == "Z-score":
        out["is_anomaly"] = out["z_anomaly"]
        out["anomaly_score"] = out["z_score"].abs()
    elif method == "Rolling statistics":
        out["is_anomaly"] = out["rolling_anomaly"] | out["stuck_anomaly"]
        out["anomaly_score"] = np.maximum(
            ((out["value"] - out["rolling_mean"]).abs() / out["rolling_std"].replace(0, np.nan))
            .fillna(0), 0
        )
    elif method == "Isolation Forest":
        out["is_anomaly"] = out["iforest_anomaly"]
        out["anomaly_score"] = out["iforest_score"]
    else:
        out["is_anomaly"] = (
            out["z_anomaly"] | out["rolling_anomaly"] |
            out["stuck_anomaly"] | out["iforest_anomaly"]
        )
        out["anomaly_score"] = np.maximum.reduce([
            out["z_score"].abs().to_numpy(),
            out["iforest_score"].to_numpy(),
            np.where(out["stuck_anomaly"], ZSCORE_THRESHOLD + 1, 0),
        ])
    return out

def anomaly_events_from_series(df: pd.DataFrame, unit_id: int, variable_id: int) -> pd.DataFrame:
    detected = detect_anomalies(df, "Combined")
    anomalies = detected[detected["is_anomaly"]].copy()
    if anomalies.empty:
        return pd.DataFrame(columns=[
            "timestamp", "unit_id", "variable_id", "value",
            "anomaly_score", "detection_method"
        ])
    methods = []
    for _, row in anomalies.iterrows():
        active = []
        if row.get("z_anomaly", False): active.append("Z_SCORE")
        if row.get("rolling_anomaly", False): active.append("ROLLING_STD")
        if row.get("stuck_anomaly", False): active.append("SENSOR_STUCK")
        if row.get("iforest_anomaly", False): active.append("ISOLATION_FOREST")
        methods.append("+".join(active) or "COMBINED")
    return pd.DataFrame({
        "timestamp": anomalies["timestamp"].values,
        "unit_id": unit_id,
        "variable_id": variable_id,
        "value": anomalies["value"].values,
        "anomaly_score": anomalies["anomaly_score"].values,
        "detection_method": methods,
    })
