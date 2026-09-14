"""Generate a realistic synthetic refinery historian and derived events."""

from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

from config import (
    ABNORMAL_EVENTS, DAYS_OF_DATA, DB_PATH, PROCESS_VARIABLES,
    RANDOM_SEED, SAMPLING_INTERVAL_MINUTES, SCHEMA_PATH, UNITS,
)
from alarm_engine import process_alarms
from anomaly_detection import anomaly_events_from_series

def build_schema(conn):
    conn.executescript(Path(SCHEMA_PATH).read_text(encoding="utf-8"))

def seed_reference_data(conn):
    for code, meta in UNITS.items():
        conn.execute(
            "INSERT INTO units(unit_code, unit_name, unit_type, description) VALUES (?, ?, ?, ?)",
            (code, meta["unit_name"], meta["unit_type"], meta["description"]),
        )
    for code, variables in PROCESS_VARIABLES.items():
        unit_id = conn.execute("SELECT unit_id FROM units WHERE unit_code=?", (code,)).fetchone()[0]
        for v in variables:
            conn.execute("""
                INSERT INTO process_variables
                (unit_id, variable_name, variable_type, engineering_unit,
                 low_limit, warning_low, normal_mean, warning_high, high_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                unit_id, v["variable_name"], v["variable_type"], v["engineering_unit"],
                v["low_limit"], v["warning_low"], v["normal_mean"],
                v["warning_high"], v["high_limit"],
            ))

def event_adjustment(event, timestamps, mean):
    start = timestamps[0] + pd.Timedelta(days=event["day"] - 1, hours=event["hour"])
    end = start + pd.Timedelta(hours=event["duration_hours"])
    active = (timestamps >= start) & (timestamps < end)
    adj = np.zeros(len(timestamps))
    typ = event["event_type"]
    if typ in {"HIGH_SPIKE", "HIGH_PRESSURE", "LOW_FLOW", "SUDDEN_SPIKE"}:
        adj[active] = event["magnitude"]
    elif typ == "GRADUAL_DRIFT":
        idx = np.where(active)[0]
        if len(idx):
            adj[idx] = np.linspace(0, event["magnitude"], len(idx))
    return adj, active

def generate_series(meta, timestamps, rng, unit_code, variable_name):
    n = len(timestamps)
    mean = meta["normal_mean"]
    noise = meta["noise_std"]
    # Low-frequency process movement + daily operating cycle + sensor noise.
    t = np.arange(n)
    slow = 0.55 * noise * np.sin(2 * np.pi * t / (24 * 60 / SAMPLING_INTERVAL_MINUTES))
    drift = 0.25 * noise * np.sin(2 * np.pi * t / (7 * 24 * 60 / SAMPLING_INTERVAL_MINUTES))
    values = mean + slow + drift + rng.normal(0, noise, n)

    # Mild process relationships within a unit.
    if unit_code == "CDU" and variable_name == "Furnace Outlet Temperature":
        values += 0.035 * (200 - 200)  # reference term; feed relationship injected below
    if unit_code in {"HDS", "NHT"} and "Hydrogen Flow" in variable_name:
        values += 0.15 * noise * np.sin(2 * np.pi * t / 288)
    return values

def main():
    rng = np.random.default_rng(RANDOM_SEED)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    end = pd.Timestamp(datetime.now().replace(second=0, microsecond=0))
    end = end.floor(f"{SAMPLING_INTERVAL_MINUTES}min")
    start = end - pd.Timedelta(days=DAYS_OF_DATA)
    timestamps = pd.date_range(start=start, end=end, freq=f"{SAMPLING_INTERVAL_MINUTES}min")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys=ON")
    build_schema(conn)
    seed_reference_data(conn)
    conn.commit()

    all_process = []
    all_alarms = []
    all_anomalies = []

    variable_ids = {}
    for code, variables in PROCESS_VARIABLES.items():
        unit_id = conn.execute("SELECT unit_id FROM units WHERE unit_code=?", (code,)).fetchone()[0]
        for v in variables:
            vid = conn.execute(
                "SELECT variable_id FROM process_variables WHERE unit_id=? AND variable_name=?",
                (unit_id, v["variable_name"]),
            ).fetchone()[0]
            variable_ids[(code, v["variable_name"])] = (unit_id, vid)

    # First generate each variable independently.
    series_map = {}
    for code, variables in PROCESS_VARIABLES.items():
        for v in variables:
            values = generate_series(v, timestamps, rng, code, v["variable_name"])
            series_map[(code, v["variable_name"])] = values

    # Add simple engineering relationships.
    if ("CDU", "Crude Feed Flow") in series_map:
        feed_delta = series_map[("CDU", "Crude Feed Flow")] - PROCESS_VARIABLES["CDU"][4]["normal_mean"]
        series_map[("CDU", "Furnace Outlet Temperature")] += 0.10 * feed_delta
        series_map[("CDU", "Overhead Flow")] += 0.08 * feed_delta
        series_map[("CDU", "Bottoms Flow")] += 0.70 * feed_delta
    if ("FCC", "Feed Flow") in series_map:
        feed_delta = series_map[("FCC", "Feed Flow")] - 100
        series_map[("FCC", "Reactor Temperature")] += 0.04 * feed_delta
        series_map[("FCC", "Main Fractionator Temperature")] += 0.02 * feed_delta
    if ("HDS", "Feed Flow") in series_map:
        feed_delta = series_map[("HDS", "Feed Flow")] - 78
        series_map[("HDS", "Hydrogen Flow")] += 0.9 * feed_delta
        series_map[("HDS", "H2/Feed Ratio")] += 0.08 * feed_delta

    # Inject known disturbances.
    for event in ABNORMAL_EVENTS:
        key = (event["unit"], event["variable"])
        if key not in series_map:
            continue
        values = series_map[key].copy()
        adj, active = event_adjustment(event, timestamps, values.mean())
        if event["event_type"] == "SENSOR_STUCK":
            idx = np.where(active)[0]
            if len(idx):
                stuck_value = values[idx[0]]
                values[idx] = stuck_value
        else:
            values += adj
        series_map[key] = values

    # Write process data in batches.
    for (code, variable_name), values in series_map.items():
        unit_id, variable_id = variable_ids[(code, variable_name)]
        rows = list(zip(
            timestamps.strftime("%Y-%m-%d %H:%M:%S"),
            [unit_id] * len(values),
            [variable_id] * len(values),
            values.round(5),
        ))
        conn.executemany(
            "INSERT INTO process_data(timestamp, unit_id, variable_id, value) VALUES (?, ?, ?, ?)",
            rows,
        )

        vmeta = next(v for v in PROCESS_VARIABLES[code] if v["variable_name"] == variable_name)
        alarm_df = process_alarms(
            timestamps, values, unit_id, variable_id,
            vmeta["low_limit"], vmeta["warning_low"], vmeta["warning_high"], vmeta["high_limit"],
        )
        if not alarm_df.empty:
            # Only the latest violating observation for a variable is considered ACTIVE.
            if alarm_df.iloc[-1]["timestamp"] >= timestamps[-1] - pd.Timedelta(minutes=SAMPLING_INTERVAL_MINUTES):
                alarm_df.loc[alarm_df.index[-1], "status"] = "ACTIVE"
            all_alarms.append(alarm_df)

        raw = pd.DataFrame({"timestamp": timestamps, "value": values})
        anomaly_df = anomaly_events_from_series(raw, unit_id, variable_id)
        if not anomaly_df.empty:
            all_anomalies.append(anomaly_df)

    if all_alarms:
        pd.concat(all_alarms, ignore_index=True).to_sql("alarms", conn, if_exists="append", index=False)
    if all_anomalies:
        pd.concat(all_anomalies, ignore_index=True).to_sql("anomaly_events", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    total_points = sum(len(v) for v in series_map.values())
    print(f"Generated {total_points:,} process observations.")
    print(f"Database: {DB_PATH}")
    print(f"Time range: {start} → {end}")
    print("Run: streamlit run app.py")

if __name__ == "__main__":
    main()
