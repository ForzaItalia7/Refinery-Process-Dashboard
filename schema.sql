PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code TEXT NOT NULL UNIQUE,
    unit_name TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS process_variables (
    variable_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    variable_type TEXT NOT NULL,
    engineering_unit TEXT NOT NULL,
    low_limit REAL NOT NULL,
    warning_low REAL NOT NULL,
    normal_mean REAL NOT NULL,
    warning_high REAL NOT NULL,
    high_limit REAL NOT NULL,
    UNIQUE(unit_id, variable_name),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);

CREATE TABLE IF NOT EXISTS process_data (
    data_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    unit_id INTEGER NOT NULL,
    variable_id INTEGER NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (variable_id) REFERENCES process_variables(variable_id)
);

CREATE TABLE IF NOT EXISTS alarms (
    alarm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    unit_id INTEGER NOT NULL,
    variable_id INTEGER NOT NULL,
    alarm_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    actual_value REAL NOT NULL,
    limit_value REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'CLEARED',
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (variable_id) REFERENCES process_variables(variable_id)
);

CREATE TABLE IF NOT EXISTS anomaly_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    unit_id INTEGER NOT NULL,
    variable_id INTEGER NOT NULL,
    value REAL NOT NULL,
    anomaly_score REAL NOT NULL,
    detection_method TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (variable_id) REFERENCES process_variables(variable_id)
);

CREATE INDEX IF NOT EXISTS idx_pd_timestamp ON process_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_pd_unit ON process_data(unit_id);
CREATE INDEX IF NOT EXISTS idx_pd_variable ON process_data(variable_id);
CREATE INDEX IF NOT EXISTS idx_pd_unit_var_ts ON process_data(unit_id, variable_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_alm_timestamp ON alarms(timestamp);
CREATE INDEX IF NOT EXISTS idx_alm_unit ON alarms(unit_id);
CREATE INDEX IF NOT EXISTS idx_alm_severity ON alarms(severity);
CREATE INDEX IF NOT EXISTS idx_alm_status ON alarms(status);

CREATE INDEX IF NOT EXISTS idx_ano_timestamp ON anomaly_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_ano_unit ON anomaly_events(unit_id);
CREATE INDEX IF NOT EXISTS idx_ano_variable ON anomaly_events(variable_id);
