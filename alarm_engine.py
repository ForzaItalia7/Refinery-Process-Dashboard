"""Process alarm classification and management."""

from typing import Tuple
import numpy as np
import pandas as pd

ALARM_TYPES = ["HIGH_ALARM", "HIGH_WARNING", "LOW_WARNING", "LOW_ALARM", "NORMAL"]
SEVERITY_MAP = {
    "HIGH_ALARM": "CRITICAL",
    "LOW_ALARM": "CRITICAL",
    "HIGH_WARNING": "HIGH",
    "LOW_WARNING": "MEDIUM",
    "NORMAL": "LOW",
}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

def classify_value(value: float, low_limit: float, warning_low: float,
                    warning_high: float, high_limit: float) -> Tuple[str, str]:
    if value >= high_limit:
        return "HIGH_ALARM", "CRITICAL"
    if value >= warning_high:
        return "HIGH_WARNING", "HIGH"
    if value <= low_limit:
        return "LOW_ALARM", "CRITICAL"
    if value <= warning_low:
        return "LOW_WARNING", "MEDIUM"
    return "NORMAL", "LOW"

def classify_series(values: np.ndarray, low_limit: float, warning_low: float,
                    warning_high: float, high_limit: float) -> Tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=float)
    alarm_types = np.full(len(values), "NORMAL", dtype=object)
    severities = np.full(len(values), "LOW", dtype=object)

    ha = values >= high_limit
    hw = (values >= warning_high) & ~ha
    la = values <= low_limit
    lw = (values <= warning_low) & ~la

    alarm_types[ha], alarm_types[hw] = "HIGH_ALARM", "HIGH_WARNING"
    alarm_types[la], alarm_types[lw] = "LOW_ALARM", "LOW_WARNING"
    severities[ha | la] = "CRITICAL"
    severities[hw] = "HIGH"
    severities[lw] = "MEDIUM"
    return alarm_types, severities

def process_alarms(timestamps, values, unit_id, variable_id,
                   low_limit, warning_low, warning_high, high_limit) -> pd.DataFrame:
    values = np.asarray(values, dtype=float)
    alarm_types, severities = classify_series(
        values, low_limit, warning_low, warning_high, high_limit
    )
    limit_map = np.select(
        [
            alarm_types == "HIGH_ALARM",
            alarm_types == "HIGH_WARNING",
            alarm_types == "LOW_ALARM",
            alarm_types == "LOW_WARNING",
        ],
        [high_limit, warning_high, low_limit, warning_low],
        default=np.nan,
    )
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps),
        "unit_id": unit_id,
        "variable_id": variable_id,
        "alarm_type": alarm_types,
        "severity": severities,
        "actual_value": values,
        "limit_value": limit_map,
        "status": "CLEARED",
    })
    return df[df["alarm_type"] != "NORMAL"].copy()

def get_plant_status(active_alarms: int, critical_alarms: int) -> str:
    if critical_alarms > 0:
        return "CRITICAL"
    if active_alarms > 0:
        return "WARNING"
    return "NORMAL"

def status_badge_html(status: str) -> str:
    colors = {
        "NORMAL": ("#d4edda", "#155724"),
        "WARNING": ("#fff3cd", "#856404"),
        "CRITICAL": ("#f8d7da", "#721c24"),
        "HIGH_WARNING": ("#fff3cd", "#856404"),
        "LOW_WARNING": ("#fff3cd", "#856404"),
        "HIGH_ALARM": ("#f8d7da", "#721c24"),
        "LOW_ALARM": ("#f8d7da", "#721c24"),
    }
    bg, fg = colors.get(status, ("#e2e3e5", "#383d41"))
    return f'<span style="background:{bg};color:{fg};padding:3px 10px;border-radius:4px;font-weight:600;font-size:.85rem">{status}</span>'
