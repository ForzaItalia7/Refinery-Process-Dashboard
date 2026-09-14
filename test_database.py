from pathlib import Path
import sqlite3

def test_schema_file_exists():
    assert Path("sql/schema.sql").exists()

def test_schema_contains_required_tables():
    sql = Path("sql/schema.sql").read_text()
    for table in ["units", "process_variables", "process_data", "alarms", "anomaly_events"]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql
