"""Streamlit refinery process monitoring dashboard."""

from datetime import timedelta
import html
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from alarm_engine import classify_value, get_plant_status
from anomaly_detection import detect_anomalies
from config import APP_ICON, APP_TITLE, DATA_LABEL, DB_PATH, TIME_RANGES, UNITS
from database import (
    get_active_alarms, get_alarm_history, get_anomalies, get_connection,
    get_kpis, get_latest_values, get_multi_variable_data, get_variables,
    initialize_database,
)

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

CSS = """
<style>
:root {
    --bg: #101316;
    --panel: #191d20;
    --panel-raised: #20262a;
    --line: #374047;
    --text: #f2f0e9;
    --muted: #9da6a8;
    --accent: #e7b85c;
    --cyan: #79c7c8;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 85% 0%, rgba(231, 184, 92, .09), transparent 28rem),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: #15191b;
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }

.block-container {
    max-width: 1500px;
    padding: 3rem 3.5rem 4rem;
}

h1, h2, h3 { letter-spacing: -.03em; font-weight: 650; }
h1 { font-size: 2.6rem; }
h2 { margin-top: 2.25rem; }

.kpi {
    background: linear-gradient(145deg, var(--panel-raised), var(--panel));
    border: 1px solid var(--line);
    border-top: 3px solid var(--accent);
    border-radius: 8px;
    padding: 18px 20px;
    min-height: 110px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, .14);
}
.kpi .value { color: var(--text); font-size: 2rem; font-weight: 700; line-height: 1.1; }
.kpi .label { color: var(--muted); font-size: .82rem; margin-top: 8px; }

.status {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(231, 184, 92, .08);
    font-weight: 700;
    font-size: .82rem;
    letter-spacing: .04em;
}
.note {
    border-left: 3px solid var(--cyan);
    border-radius: 0 6px 6px 0;
    padding: 11px 14px;
    background: rgba(121, 199, 200, .08);
    color: #c9d4d2;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption { color: var(--muted); }
[data-baseweb="select"] > div,
[data-testid="stTextInput"] input {
    background: var(--panel);
    border-color: var(--line);
    border-radius: 6px;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow: hidden;
}
[data-testid="stPlotlyChart"] {
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 6px;
    background: rgba(25, 29, 32, .65);
}

.stDownloadButton button {
    border: 1px solid var(--accent);
    color: var(--accent);
    background: transparent;
    border-radius: 6px;
}
.stDownloadButton button:hover {
    color: var(--bg);
    background: var(--accent);
    border-color: var(--accent);
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_resource
def ensure_db():
    initialize_database()
    return True

ensure_db()

def db_has_data():
    try:
        with get_connection() as conn:
            n = conn.execute("SELECT COUNT(*) FROM process_data").fetchone()[0]
        return n > 0
    except sqlite3.Error:
        return False

if not db_has_data():
    st.error("No process database was found. Generate the synthetic historian first.")
    st.code("python generate_data.py", language="bash")
    st.stop()

@st.cache_data(ttl=30)
def cached_latest():
    return get_latest_values()

@st.cache_data(ttl=30)
def cached_variables(unit_id=None):
    return get_variables(unit_id)

@st.cache_data(ttl=30)
def cached_alarm_history(unit, severity, start, end):
    return get_alarm_history(unit, severity, start, end)

@st.cache_data(ttl=30)
def cached_anomalies(unit, start, end):
    return get_anomalies(unit, start, end)

st.sidebar.title("Operations")
page = st.sidebar.radio(
    "View",
    ["Plant overview", "Process trends", "Alarm management",
     "Anomaly detection", "Process relationships", "Unit comparison"],
)
st.sidebar.caption(DATA_LABEL)

units = ["All Units"] + list(UNITS.keys())
selected_unit = st.sidebar.selectbox("Unit", units)

range_label = st.sidebar.selectbox("Time range", list(TIME_RANGES.keys()), index=2)
hours = TIME_RANGES[range_label]
end_time = pd.Timestamp.now().floor("min")
start_time = end_time - pd.Timedelta(hours=hours)

def title_block(title, subtitle=""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

def kpi(label, value):
    st.markdown(f'<div class="kpi"><div class="value">{html.escape(str(value))}</div><div class="label">{html.escape(label)}</div></div>', unsafe_allow_html=True)

def status_for_row(row):
    alarm, severity = classify_value(
        float(row["value"]), float(row["low_limit"]), float(row["warning_low"]),
        float(row["warning_high"]), float(row["high_limit"])
    )
    return alarm, severity

def filtered_variables():
    if selected_unit == "All Units":
        return cached_variables()
    unit_id = int(cached_variables().query("unit_code == @selected_unit").iloc[0]["unit_id"])
    return cached_variables(unit_id)

latest = cached_latest()
if selected_unit != "All Units":
    latest = latest[latest["unit_code"] == selected_unit].copy()

active = get_active_alarms(selected_unit, None, 1000)
critical = active[active["severity"] == "CRITICAL"]

if page == "Plant overview":
    title_block("Plant operations", "Current process state, alarms, and operating-limit performance")
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Monitored units", len(UNITS))
    with c2: kpi("Process variables", len(cached_variables()))
    with c3: kpi("Active alarms", len(active))
    with c4: kpi("Critical alarms", len(critical))

    status = get_plant_status(len(active), len(critical))
    badge = {"NORMAL":"#8bd5a5","WARNING":"#f4c95d","CRITICAL":"#ff7b72"}[status]
    st.markdown(
        f'<div class="status" style="border-color:{badge};color:{badge}">Plant status · {status}</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(f'<div class="note">{html.escape(DATA_LABEL)}</div>', unsafe_allow_html=True)

    st.subheader("Current operating conditions")
    if latest.empty:
        st.info("No current measurements.")
    else:
        display = latest.copy()
        display["status"] = display.apply(lambda r: status_for_row(r)[0], axis=1)
        display["value"] = display["value"].round(3)
        display = display[[
            "unit_code","variable_name","value","engineering_unit",
            "warning_low","warning_high","low_limit","high_limit","status"
        ]]
        display.columns = [
    "Unit",
    "Variable",
    "Current",
    "Engineering Unit",
    "Warn Low",
    "Warn High",
    "Low Alarm",
    "High Alarm",
    "Status",
]
        st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Recent active alarms")
    st.dataframe(active.head(15), use_container_width=True, hide_index=True)

elif page == "Process trends":
    title_block("Process trends", "Historian-style time series with operating and statistical limits")
    vars_df = filtered_variables()
    if vars_df.empty:
        st.info("No variables available.")
        st.stop()

    labels = [
        f'{r.variable_name} [{r.engineering_unit}]'
        for r in vars_df.itertuples()
    ]
    selected_label = st.selectbox("Process variable", labels)
    row = vars_df.iloc[labels.index(selected_label)]
    data = get_multi_variable_data([int(row.variable_id)], start_time, end_time)
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    if data.empty:
        st.info("No data in the selected time window.")
    else:
        mean = data["value"].mean()
        std = data["value"].std(ddof=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.timestamp, y=data.value, mode="lines", name=row.variable_name))
        for y, name, dash in [
            (row.high_limit, "High alarm", "dash"),
            (row.warning_high, "High warning", "dot"),
            (row.normal_mean, "Target", "solid"),
            (row.warning_low, "Low warning", "dot"),
            (row.low_limit, "Low alarm", "dash"),
            (mean + 3*std, "SPC UCL", "dashdot"),
            (mean - 3*std, "SPC LCL", "dashdot"),
        ]:
            fig.add_hline(y=float(y), line_dash=dash, annotation_text=name, annotation_position="top left")
        fig.update_layout(height=520, margin=dict(l=20,r=20,t=35,b=20), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        inside = data["value"].between(row.warning_low, row.warning_high).mean()*100
        a,b,c,d = st.columns(4)
        with a: kpi("Average", f"{mean:.2f} {row.engineering_unit}")
        with b: kpi("Minimum", f"{data.value.min():.2f}")
        with c: kpi("Maximum", f"{data.value.max():.2f}")
        with d: kpi("Within warning band", f"{inside:.1f}%")

        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered trend CSV", csv, "process_trend.csv", "text/csv")

elif page == "Alarm management":
    title_block("Alarm management", "Operating-limit violations and alarm history")
    severity = st.selectbox("Severity", ["All","CRITICAL","HIGH","MEDIUM","LOW"])
    alarms = cached_alarm_history(selected_unit, severity, start_time, end_time)
    c1,c2,c3 = st.columns(3)
    with c1: kpi("Events in range", len(alarms))
    with c2: kpi("Critical events", int((alarms.severity=="CRITICAL").sum()) if not alarms.empty else 0)
    with c3: kpi("High-warning events", int((alarms.severity=="HIGH").sum()) if not alarms.empty else 0)

    if not alarms.empty:
        col1,col2 = st.columns(2)
        with col1:
            counts = alarms.groupby("unit_code").size().reset_index(name="count").sort_values("count", ascending=False)
            st.plotly_chart(px.bar(counts, x="unit_code", y="count", title="Alarm events by unit"), use_container_width=True)
        with col2:
            counts = alarms.groupby("severity").size().reset_index(name="count")
            st.plotly_chart(px.bar(counts, x="severity", y="count", title="Alarm events by severity"), use_container_width=True)
        st.dataframe(alarms, use_container_width=True, hide_index=True)
        st.download_button("Download alarm history CSV", alarms.to_csv(index=False).encode(), "alarm_history.csv", "text/csv")
    else:
        st.success("No alarm events in the selected window.")

elif page == "Anomaly detection":
    title_block("Anomaly detection", "Statistical deviations from normal process behavior")
    method = st.selectbox("Detection method", ["Combined","Z-score","Rolling statistics","Isolation Forest"])
    vars_df = filtered_variables()
    labels = [f'{r.variable_name} [{r.engineering_unit}]' for r in vars_df.itertuples()]
    selected_label = st.selectbox("Variable", labels)
    row = vars_df.iloc[labels.index(selected_label)]
    data = get_multi_variable_data([int(row.variable_id)], start_time, end_time)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    if len(data) < 20:
        st.warning("Select a longer time window for statistical detection.")
    else:
        detected = detect_anomalies(data[["timestamp","value"]], method)
        anomalies = detected[detected["is_anomaly"]]
        c1,c2,c3 = st.columns(3)
        with c1: kpi("Observations", len(detected))
        with c2: kpi("Anomalies", len(anomalies))
        with c3: kpi("Anomaly rate", f"{100*len(anomalies)/len(detected):.2f}%")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=detected.timestamp, y=detected.value, mode="lines", name="Process value"))
        if not anomalies.empty:
            fig.add_trace(go.Scatter(
                x=anomalies.timestamp, y=anomalies.value, mode="markers",
                marker=dict(size=8, symbol="x"), name="Anomaly"
            ))
        fig.update_layout(height=500, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Z-score flags values far from the global mean; rolling statistics detect local deviations; Isolation Forest detects unusual observations. Statistical limits are not safety-system limits.")

        if not anomalies.empty:
            out = anomalies[["timestamp","value","anomaly_score"]].sort_values("timestamp", ascending=False)
            st.dataframe(out, use_container_width=True, hide_index=True)
            st.download_button("Download anomaly CSV", out.to_csv(index=False).encode(), "anomalies.csv", "text/csv")

elif page == "Process relationships":
    title_block("Process relationships", "Explore correlations between variables within a refinery unit")
    vars_df = filtered_variables()
    if len(vars_df) < 2:
        st.info("Select a unit containing at least two variables.")
        st.stop()
    selected = st.multiselect(
        "Variables for correlation matrix",
        vars_df.variable_name.tolist(),
        default=vars_df.variable_name.tolist()[:min(6,len(vars_df))],
    )
    chosen = vars_df[vars_df.variable_name.isin(selected)]
    data = get_multi_variable_data(chosen.variable_id.tolist(), start_time, end_time)
    if data.empty:
        st.info("No data.")
    else:
        pivot = data.pivot_table(index="timestamp", columns="variable_name", values="value", aggfunc="mean")
        corr = pivot.corr()
        st.plotly_chart(px.imshow(corr, text_auto=".2f", aspect="auto", title="Pearson correlation matrix"), use_container_width=True)
        if len(selected) >= 2:
            a,b = st.columns(2)
            with a: xvar = st.selectbox("X variable", selected)
            with b: yvar = st.selectbox("Y variable", [v for v in selected if v != xvar])
            xy = pivot[[xvar,yvar]].dropna()
            r = xy[xvar].corr(xy[yvar])
            fig = px.scatter(xy, x=xvar, y=yvar, trendline="ols", title=f"{xvar} vs {yvar} · r = {r:.3f}")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Unit comparison":
    title_block("Unit comparison", "Compare operating performance across refinery units")
    kpis = get_kpis(selected_unit, start_time, end_time)
    if kpis.empty:
        st.info("No KPI data.")
    else:
        summary = kpis.groupby("unit_code").agg(
            avg_value=("average_value","mean"),
            variables=("variable_name","count"),
            within_limits=("pct_within_limits","mean"),
        ).reset_index()
        alarms = get_alarm_history(selected_unit, "All", start_time, end_time)
        alarm_counts = alarms.groupby("unit_code").size().rename("alarm_count") if not alarms.empty else pd.Series(dtype=float)
        summary["alarm_count"] = summary["unit_code"].map(alarm_counts).fillna(0)
        anomalies = get_anomalies(selected_unit, start_time, end_time)
        anomaly_counts = anomalies.groupby("unit_code").size().rename("anomaly_count") if not anomalies.empty else pd.Series(dtype=float)
        summary["anomaly_count"] = summary["unit_code"].map(anomaly_counts).fillna(0)

        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(px.bar(summary, x="unit_code", y="alarm_count", title="Alarm events by unit"), use_container_width=True)
        with c2: st.plotly_chart(px.bar(summary, x="unit_code", y="anomaly_count", title="Anomalies by unit"), use_container_width=True)
        st.dataframe(summary.round(2), use_container_width=True, hide_index=True)
