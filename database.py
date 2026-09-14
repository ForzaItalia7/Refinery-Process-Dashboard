"""SQLite access layer for the refinery dashboard."""

import sqlite3
from pathlib import Path
import pandas as pd
from config import DB_PATH, SCHEMA_PATH

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with get_connection() as conn:
        conn.executescript(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
        conn.commit()

def clear_database():
    initialize_database()
    with get_connection() as conn:
        for table in ("anomaly_events", "alarms", "process_data", "process_variables", "units"):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()

def get_units():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT unit_id, unit_code, unit_name, unit_type, description FROM units ORDER BY unit_id",
            conn,
        )

def get_unit_id(unit_code):
    with get_connection() as conn:
        row = conn.execute("SELECT unit_id FROM units WHERE unit_code = ?", (unit_code,)).fetchone()
    return row[0] if row else None

def get_variables(unit_id=None):
    sql = """
        SELECT pv.*, u.unit_code, u.unit_name
        FROM process_variables pv
        JOIN units u ON u.unit_id = pv.unit_id
    """
    params = ()
    if unit_id is not None:
        sql += " WHERE pv.unit_id = ?"
        params = (unit_id,)
    sql += " ORDER BY u.unit_code, pv.variable_name"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_variable_limits(variable_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT low_limit, warning_low, normal_mean, warning_high, high_limit, engineering_unit
            FROM process_variables WHERE variable_id = ?
        """, (variable_id,)).fetchone()
    return row

def get_latest_values(unit_id=None):
    sql = """
    SELECT u.unit_code, u.unit_name, pv.variable_id, pv.variable_name,
           pv.engineering_unit, pv.low_limit, pv.warning_low, pv.normal_mean,
           pv.warning_high, pv.high_limit, pd.timestamp, pd.value
    FROM process_data pd
    JOIN process_variables pv ON pv.variable_id = pd.variable_id
    JOIN units u ON u.unit_id = pd.unit_id
    WHERE pd.data_id IN (
        SELECT MAX(data_id) FROM process_data GROUP BY variable_id
    )
    """
    params = ()
    if unit_id is not None:
        sql += " AND pd.unit_id = ?"
        params = (unit_id,)
    sql += " ORDER BY u.unit_code, pv.variable_name"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_process_data(unit_id, variable_id, start_time=None, end_time=None):
    sql = """
        SELECT pd.timestamp, pd.value
        FROM process_data pd
        WHERE pd.unit_id = ? AND pd.variable_id = ?
    """
    params = [unit_id, variable_id]
    if start_time is not None:
        sql += " AND pd.timestamp >= ?"
        params.append(pd.Timestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"))
    if end_time is not None:
        sql += " AND pd.timestamp <= ?"
        params.append(pd.Timestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"))
    sql += " ORDER BY pd.timestamp"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_multi_variable_data(variable_ids, start_time=None, end_time=None):
    if not variable_ids:
        return pd.DataFrame()
    placeholders = ",".join("?" * len(variable_ids))
    sql = f"""
        SELECT pd.timestamp, pd.value, pd.unit_id, pd.variable_id,
               u.unit_code, pv.variable_name, pv.engineering_unit
        FROM process_data pd
        JOIN units u ON u.unit_id = pd.unit_id
        JOIN process_variables pv ON pv.variable_id = pd.variable_id
        WHERE pd.variable_id IN ({placeholders})
    """
    params = list(variable_ids)
    if start_time is not None:
        sql += " AND pd.timestamp >= ?"
        params.append(pd.Timestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"))
    if end_time is not None:
        sql += " AND pd.timestamp <= ?"
        params.append(pd.Timestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"))
    sql += " ORDER BY pd.timestamp"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_active_alarms(unit_code=None, severity=None, limit=500):
    sql = """
    SELECT a.alarm_id, a.timestamp, u.unit_code, u.unit_name,
           pv.variable_name, pv.engineering_unit, a.alarm_type,
           a.severity, a.actual_value, a.limit_value, a.status
    FROM alarms a
    JOIN units u ON u.unit_id = a.unit_id
    JOIN process_variables pv ON pv.variable_id = a.variable_id
    WHERE a.status = 'ACTIVE'
    """
    params = []
    if unit_code and unit_code != "All Units":
        sql += " AND u.unit_code = ?"
        params.append(unit_code)
    if severity and severity != "All":
        sql += " AND a.severity = ?"
        params.append(severity)
    sql += " ORDER BY a.timestamp DESC LIMIT ?"
    params.append(int(limit))
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_alarm_history(unit_code=None, severity=None, start_time=None, end_time=None):
    sql = """
    SELECT a.alarm_id, a.timestamp, u.unit_code, u.unit_name,
           pv.variable_name, pv.engineering_unit, a.alarm_type,
           a.severity, a.actual_value, a.limit_value, a.status
    FROM alarms a
    JOIN units u ON u.unit_id = a.unit_id
    JOIN process_variables pv ON pv.variable_id = a.variable_id
    WHERE 1=1
    """
    params = []
    if unit_code and unit_code != "All Units":
        sql += " AND u.unit_code = ?"; params.append(unit_code)
    if severity and severity != "All":
        sql += " AND a.severity = ?"; params.append(severity)
    if start_time is not None:
        sql += " AND a.timestamp >= ?"; params.append(pd.Timestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"))
    if end_time is not None:
        sql += " AND a.timestamp <= ?"; params.append(pd.Timestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"))
    sql += " ORDER BY a.timestamp DESC"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_alarm_summary():
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT u.unit_code, a.severity, COUNT(*) AS alarm_count
            FROM alarms a JOIN units u ON u.unit_id = a.unit_id
            GROUP BY u.unit_code, a.severity
            ORDER BY alarm_count DESC
        """, conn)

def get_anomalies(unit_code=None, start_time=None, end_time=None, limit=None):
    sql = """
    SELECT ae.event_id, ae.timestamp, u.unit_code, u.unit_name,
           pv.variable_name, pv.engineering_unit, ae.value,
           ae.anomaly_score, ae.detection_method
    FROM anomaly_events ae
    JOIN units u ON u.unit_id = ae.unit_id
    JOIN process_variables pv ON pv.variable_id = ae.variable_id
    WHERE 1=1
    """
    params = []
    if unit_code and unit_code != "All Units":
        sql += " AND u.unit_code = ?"; params.append(unit_code)
    if start_time is not None:
        sql += " AND ae.timestamp >= ?"; params.append(pd.Timestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"))
    if end_time is not None:
        sql += " AND ae.timestamp <= ?"; params.append(pd.Timestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"))
    sql += " ORDER BY ae.timestamp DESC"
    if limit:
        sql += " LIMIT ?"; params.append(int(limit))
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_kpis(unit_code=None, start_time=None, end_time=None):
    sql = """
    SELECT u.unit_code, pv.variable_name, pv.engineering_unit,
           AVG(pd.value) AS average_value,
           MIN(pd.value) AS minimum_value,
           MAX(pd.value) AS maximum_value,
           COUNT(*) AS observations,
           AVG(CASE WHEN pd.value BETWEEN pv.warning_low AND pv.warning_high THEN 1.0 ELSE 0.0 END) * 100 AS pct_within_limits
    FROM process_data pd
    JOIN units u ON u.unit_id = pd.unit_id
    JOIN process_variables pv ON pv.variable_id = pd.variable_id
    WHERE 1=1
    """
    params = []
    if unit_code and unit_code != "All Units":
        sql += " AND u.unit_code = ?"; params.append(unit_code)
    if start_time is not None:
        sql += " AND pd.timestamp >= ?"; params.append(pd.Timestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"))
    if end_time is not None:
        sql += " AND pd.timestamp <= ?"; params.append(pd.Timestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"))
    sql += " GROUP BY u.unit_code, pv.variable_id ORDER BY u.unit_code, pv.variable_name"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)
