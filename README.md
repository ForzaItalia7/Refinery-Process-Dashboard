🏭 Refinery Process Monitoring Dashboard

An interactive refinery process monitoring and analytics dashboard built using Python, SQL, SQLite, Pandas, Plotly, and Streamlit.

The project simulates historian-style process data from multiple refinery units and provides operators/engineers with a centralized view of process conditions, KPIs, alarms, anomalies, historical trends, and variable relationships.

⚠️ Note: This project uses synthetic/simulated refinery data for educational and portfolio purposes. It is not connected to a live refinery, DCS, SCADA, PLC, or safety system.

📌 Project Overview

Refinery operations generate large volumes of time-series process data such as:

Temperature
Pressure
Flow rate
Composition
Process ratios
Product quality measurements

This project models that data using a relational SQLite database and provides a Streamlit interface for monitoring process behavior.

The system can:

Monitor current operating conditions
Track process variables over time
Identify operating-limit violations
Generate high/low alarms
Detect statistical anomalies
Analyze process variability
Compare refinery units
Explore correlations between process variables
Export filtered data and reports
🏗️ System Architecture
              Synthetic Process Model
                       │
                       ▼
              ┌─────────────────┐
              │ generate_data.py│
              └────────┬────────┘
                       │
                       ▼
                ┌─────────────┐
                │   SQLite    │
                │  Historian  │
                └──────┬──────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
    process_data     alarms    anomaly_events
          │            │            │
          └────────────┼────────────┘
                       ▼
                ┌─────────────┐
                │ database.py │
                └──────┬──────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Alarm Engine        Anomaly Detection
             │                   │
             └─────────┬─────────┘
                       ▼
              ┌─────────────────┐
              │    Streamlit    │
              │    Dashboard    │
              └────────┬────────┘
                       │
                       ▼
             Interactive Analytics
🏭 Refinery Units

The dashboard models six refinery units:

Code	Unit	Type
CDU	Crude Distillation Unit	Distillation
VDU	Vacuum Distillation Unit	Distillation
FCC	Fluid Catalytic Cracking Unit	Cracking
HDS	Hydrodesulfurization Unit	Treating
NHT	Naphtha Hydrotreater	Treating
REF	Catalytic Reformer	Reforming

Each unit contains multiple process variables with engineering units, normal operating values, warning limits, and alarm limits.

📊 Dashboard Features
1. Plant Overview

The main dashboard provides a high-level view of plant conditions.

KPIs
Number of monitored units
Number of process variables
Active alarms
Critical alarms

The overall plant condition is classified as:

NORMAL
WARNING
CRITICAL

based on active process alarms.

The dashboard also displays the latest operating condition of each monitored variable.

2. Process Trend Analysis

Users can select a process variable and time period to investigate historical behavior.

Supported time ranges include:

Last 1 hour
Last 6 hours
Last 24 hours
Last 7 days
Last 30 days

Interactive Plotly charts display:

Process measurement
High alarm limit
Low alarm limit
High warning limit
Low warning limit
Target operating value
Statistical control limits

This allows process deviations and long-term trends to be identified visually.

🚨 3. Alarm Management

The alarm engine classifies process measurements against configurable operating limits.

Each variable has:

Low Alarm
Low Warning
Normal Operating Region
High Warning
High Alarm
Alarm classification
value >= high_limit
        ↓
HIGH_ALARM / CRITICAL

warning_high <= value < high_limit
        ↓
HIGH_WARNING / HIGH

warning_low < value <= low_limit
        ↓
LOW_ALARM / CRITICAL

low_limit < value <= warning_low
        ↓
LOW_WARNING / MEDIUM

otherwise
        ↓
NORMAL

The alarm dashboard provides:

Alarm history
Alarm severity filtering
Alarm count by refinery unit
Alarm count by severity
Detailed alarm table
CSV export

The alarm engine also uses vectorized NumPy operations for efficient classification of large time-series datasets.

🔎 4. Statistical Anomaly Detection

The project implements multiple anomaly-detection techniques.

Z-Score

For a process variable:

z = (x - μ) / σ

A measurement is flagged when:

|z| > 3

This identifies observations that are significantly different from the overall process distribution.

Rolling Statistics

A rolling window is used to identify deviations from recent process behavior.

The default configuration uses:

12 samples × 5 minutes = 1 hour

A point is flagged when it falls outside:

Rolling Mean ± 3 × Rolling Standard Deviation

This is useful for identifying local process disturbances that may not appear extreme relative to the entire 30-day dataset.

Isolation Forest

An unsupervised Isolation Forest model is also implemented to identify unusual observations.

This provides a machine-learning-based complement to traditional statistical techniques.

Sensor-Stuck Detection

The system also checks for measurements with almost zero variation over a rolling window.

This can identify a possible:

SENSOR_STUCK

condition.

📈 5. Statistical Process Control

The dashboard calculates simplified statistical control limits:

UCL = μ + 3σ

LCL = μ - 3σ

These are visualized alongside the process trend.

Important distinction

SPC control limits describe statistical process behavior.

They are not equivalent to:

Safety instrumented system trips
Emergency shutdown limits
DCS interlocks
Actual refinery safety limits
🔗 6. Process Relationships

The dashboard provides correlation analysis between process variables.

Users can:

Select multiple variables
Generate a correlation matrix
Compare two variables
View a scatter plot
Calculate the Pearson correlation coefficient

Example relationships include:

Feed Flow ↔ Reactor Temperature

Pressure ↔ Temperature

Hydrogen Flow ↔ H₂/Feed Ratio

The synthetic data generator also introduces selected relationships between process variables instead of treating every measurement as completely independent.

🏭 7. Unit Comparison

Different refinery units can be compared using:

Average process values
Number of monitored variables
Percentage within operating limits
Alarm events
Anomaly events

This provides a plant-level view of where abnormal behavior is concentrated.

🗄️ Database Design

The application uses SQLite as a lightweight relational historian database.

units

Stores refinery-unit information.

unit_id
unit_code
unit_name
unit_type
description
process_variables

Stores process tags and their engineering limits.

variable_id
unit_id
variable_name
variable_type
engineering_unit
low_limit
warning_low
normal_mean
warning_high
high_limit
process_data

Stores timestamped process measurements.

data_id
timestamp
unit_id
variable_id
value
alarms

Stores process-limit violations.

alarm_id
timestamp
unit_id
variable_id
alarm_type
severity
actual_value
limit_value
status
anomaly_events

Stores detected statistical anomalies.

event_id
timestamp
unit_id
variable_id
value
anomaly_score
detection_method

Indexes are implemented on frequently queried fields such as:

timestamp
unit_id
variable_id
(unit_id, variable_id, timestamp)
🧪 Synthetic Historian Data

The project generates approximately 30 days of process data at 5-minute intervals.

The generator incorporates:

Normal operating means
Process noise
Periodic variation
Gradual process movement
Relationships between variables
Process disturbances
Sensor abnormalities

It deliberately injects abnormal operating scenarios so that the monitoring and anomaly-detection functionality can be demonstrated.

Injected scenarios include
FCC reactor temperature high excursion
CDU crude feed-flow reduction
HDS reactor pressure increase
CDU furnace-temperature gradual drift
VDU column-pressure spike
FCC regenerator-temperature excursion
NHT temperature sensor stuck condition
HDS feed-flow reduction
Reformer reactor inlet temperature excursion
📁 Project Structure
refinery-process-dashboard/
│
├── app.py
├── config.py
├── database.py
├── generate_data.py
├── alarm_engine.py
├── anomaly_detection.py
├── requirements.txt
├── README.md
│
├── data/
│   └── refinery.db
│
├── sql/
│   └── schema.sql
│
└── tests/
    ├── test_alarm_engine.py
    ├── test_anomaly_detection.py
    └── test_database.py
🛠️ Technologies
Programming
Python
Database
SQLite
SQL
Data Processing
Pandas
NumPy
Visualization
Plotly
Streamlit
Machine Learning
Scikit-learn
Isolation Forest
Testing
Pytest
🚀 Installation
1. Clone the repository
git clone <your-repository-url>
cd refinery-process-dashboard
2. Create a virtual environment
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
Windows
python -m venv .venv
.venv\Scripts\activate
3. Install dependencies
python -m pip install -r requirements.txt
▶️ Running the Application

The repository can contain the generated SQLite database.

If the database is already present:

python -m streamlit run app.py

The application will be available at:

http://localhost:8501
Generating a New Dataset

To regenerate the synthetic refinery historian:

python generate_data.py

This recreates:

data/refinery.db

with the configured historical dataset and injected abnormal events.

Then start Streamlit:

python -m streamlit run app.py
🧪 Running Tests

Run:

pytest -q

The test suite covers:

Alarm classification
Vectorized alarm classification
Plant-status calculation
Z-score anomaly detection
Empty-data handling
Database schema
Required database tables
💡 Engineering Concepts Demonstrated

This project combines chemical/process engineering concepts with software and data engineering.

Process Engineering
Refinery unit operations
Process variables
Operating ranges
Process disturbances
Alarm limits
Process monitoring
Statistical process control
Data Engineering
Relational database design
Time-series data
SQL queries
Database indexing
Aggregation
Filtered data retrieval
Data Science
Z-score analysis
Rolling statistics
Anomaly detection
Isolation Forest
Correlation analysis
Process variability analysis
Software Engineering
Modular Python architecture
Configuration management
Database abstraction
Automated testing
Interactive web application
Data export
⚠️ Limitations

This is a portfolio/educational simulation and does not represent a production refinery monitoring system.

It does not implement:

DCS integration
SCADA integration
PLC communication
Real-time control
Safety Instrumented Systems
Production-grade authentication
Cybersecurity controls
Redundant databases
Real refinery operating constraints

The alarm limits and process values are synthetic engineering-style demonstration values.

🎯 Future Improvements

Potential extensions include:

Live MQTT/Kafka historian streaming
PostgreSQL/TimescaleDB backend
Real-time data ingestion
User authentication and role-based access
Alarm acknowledgement workflow
Alarm shelving
Equipment health monitoring
Predictive maintenance
Multivariate anomaly detection
Advanced SPC rules
Process unit PFD visualization
Docker deployment
Cloud deployment
REST API for process data
👨‍💻 Project Motivation

The project was designed to demonstrate how process engineering knowledge can be combined with software engineering and data analytics to build practical industrial monitoring applications.

Rather than treating process measurements as isolated datasets, the system models:

Process Variables
       ↓
Historian Data
       ↓
Operating Limits
       ↓
Alarms
       ↓
Statistical Analysis
       ↓
Anomaly Detection
       ↓
Engineering Decision Support
📌 Portfolio Description

Refinery Process Monitoring Dashboard — Developed an interactive refinery process monitoring dashboard using Python, SQL/SQLite and Streamlit, modeling 30 days of 5-minute historian data across six refinery units. Implemented relational time-series data storage, vectorized process alarms, KPI monitoring, historical trend analysis, SPC limits, Z-score/rolling-statistics/Isolation Forest anomaly detection, correlation analysis and configurable operating-limit visualization.
