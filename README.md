# 🏭 Refinery Process Monitoring Dashboard

An interactive **process monitoring and alarm management dashboard** for refinery operations, built using **Python, SQL, Streamlit, Pandas, Plotly, and Scikit-learn**.

The project simulates time-series process data from multiple refinery units and provides tools for monitoring operating conditions, identifying abnormal behavior, analyzing process relationships, and managing process alarms.

---

## 🚀 Features

- 📊 **Plant Overview**
  - Real-time-style plant KPIs
  - Unit operating status
  - Active alarm summary
  - Overall plant health indication

- 📈 **Process Trend Analysis**
  - Interactive temperature, pressure, flow and other process-variable trends
  - Configurable time ranges
  - Unit and variable filtering
  - Historical process visualization

- 🚨 **Alarm Management**
  - High/low warning limits
  - High/low critical alarm limits
  - Alarm severity classification
  - Historical alarm analysis

- 🔍 **Anomaly Detection**
  - Statistical Z-score detection
  - Rolling mean and standard deviation analysis
  - Stuck-sensor detection
  - Isolation Forest for multivariate-style anomaly detection

- 🔗 **Process Relationships**
  - Correlation analysis between process variables
  - Scatter plots and relationship analysis
  - Identification of strongly related process parameters

- ⚖️ **Unit Comparison**
  - Compare operating conditions across refinery units
  - Variable-wise statistical comparison
  - Identify units operating outside expected ranges

- 📥 **Data Export**
  - Export filtered process data, alarms and anomaly results as CSV files

---

## 🏗️ System Architecture

```text
Synthetic Process Data
        ↓
Data Generation & Event Injection
        ↓
SQLite Database
        ↓
┌───────────────────────────────┐
│       Monitoring Engine       │
│                               │
│  • Alarm Detection            │
│  • Anomaly Detection          │
│  • Statistical Analysis       │
│  • Process Relationships      │
└───────────────────────────────┘
        ↓
Streamlit Dashboard
        ↓
KPIs • Trends • Alarms • Anomalies
• Correlations • Unit Comparison
