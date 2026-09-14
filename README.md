# Refinery Process Monitoring Dashboard

A portfolio-grade **synthetic refinery historian and process-monitoring dashboard** built with Python, SQL/SQLite, Pandas, Plotly and Streamlit.

> The process data is simulated for demonstration. This application is not connected to a DCS, SCADA, PLC or live refinery control system.

## What it demonstrates

- Relational SQL design for time-series process data
- 30 days of 5-minute synthetic historian data
- Six refinery units and 40+ process variables
- Engineering-style operating and alarm limits
- High/low warning and alarm classification
- KPI monitoring and historical trends
- Z-score anomaly detection
- Rolling-statistics anomaly detection
- Isolation Forest anomaly detection
- Sensor-stuck detection
- Statistical process control limits
- Correlation analysis
- Unit comparison
- CSV export
- Automated tests

## Architecture

```text
Synthetic process model
        |
        v
generate_data.py
        |
        v
SQLite historian
  |       |       |
  |       |       +--> anomaly_events
  |       +----------> alarms
  +------------------> process_data
        |
        v
database.py
        |
        +--> alarm_engine.py
        +--> anomaly_detection.py
        |
        v
Streamlit + Plotly
```

## Database

### units
Refinery operating units.

### process_variables
Tags, engineering units, operating targets and warning/alarm limits.

### process_data
Timestamped historian observations.

### alarms
Operating-limit violations. Historical events are stored as `CLEARED`; an alarm condition at the latest historian point can be `ACTIVE`.

### anomaly_events
Statistical anomalies produced during data generation.

Indexes are provided on timestamps, units, variables and common composite filters.

## Units

- CDU — Crude Distillation Unit
- VDU — Vacuum Distillation Unit
- FCC — Fluid Catalytic Cracking Unit
- HDS — Hydrodesulfurization Unit
- NHT — Naphtha Hydrotreater
- REF — Catalytic Reformer

## Synthetic process behavior

The generator does not use independent random numbers alone. It combines:

- normal operating means
- process noise
- slow movement
- daily/weekly variation
- simple process relationships
- deliberate abnormal events

Injected scenarios include:

- FCC reactor temperature high spike
- CDU feed-flow reduction
- HDS reactor-pressure increase
- CDU furnace-temperature drift
- VDU pressure spike
- FCC regenerator-temperature spike
- NHT sensor stuck condition
- HDS feed-flow reduction
- reformer reactor-inlet temperature spike

## Alarm logic

For every variable:

```text
value >= high_limit       -> HIGH_ALARM / CRITICAL
warning_high <= value     -> HIGH_WARNING / HIGH
value <= low_limit        -> LOW_ALARM / CRITICAL
value <= warning_low      -> LOW_WARNING / MEDIUM
otherwise                 -> NORMAL
```

These limits are demonstration operating limits, not SIS trip settings.

## Anomaly detection

### Z-score

```text
z = (x - mean) / standard_deviation
```

A point is flagged when `|z| > 3`.

### Rolling statistics

A one-hour rolling window is used for the default 5-minute sampling rate. Local deviations beyond three rolling standard deviations are flagged.

### Isolation Forest

Isolation Forest provides a model-based unsupervised detector for unusual observations.

### Sensor stuck

A near-zero rolling standard deviation over the configured window flags a potentially stuck sensor.

### SPC distinction

The dashboard also shows:

```text
UCL = mean + 3 sigma
LCL = mean - 3 sigma
```

SPC control limits describe statistical behavior; they are not the same thing as process safety or alarm limits.

## Setup

### 1. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the database

```bash
python generate_data.py
```

This creates:

```text
data/refinery.db
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

### 5. Run tests

```bash
pytest -q
```

## Suggested interview explanation

"I built a synthetic refinery process-monitoring application around a SQLite historian. I modeled units, process tags, operating limits, timestamped measurements, alarms and anomaly events as relational tables. The generator creates correlated 5-minute process data and injects known disturbances such as temperature spikes, flow reductions, pressure excursions, drift and a stuck sensor. SQL is used for filtered retrieval and aggregation before the data reaches Pandas. The dashboard then provides KPI monitoring, trend visualization, configurable alarm classification and statistical anomaly detection."

## Important limitations

This is an educational/portfolio model. It does not implement:

- DCS/SCADA communications
- PLC integration
- real-time control
- safety instrumented functions
- authenticated users
- production database high availability
- real refinery operating constraints

Those limitations should be stated honestly in interviews.
