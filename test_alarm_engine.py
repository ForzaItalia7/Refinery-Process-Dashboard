import numpy as np
from alarm_engine import classify_value, classify_series, get_plant_status

def test_scalar_classification():
    assert classify_value(100, 0, 10, 90, 100) == ("HIGH_ALARM", "CRITICAL")
    assert classify_value(95, 0, 10, 90, 100) == ("HIGH_WARNING", "HIGH")
    assert classify_value(0, 0, 10, 90, 100) == ("LOW_ALARM", "CRITICAL")
    assert classify_value(15, 0, 10, 90, 100) == ("NORMAL", "LOW")

def test_vector_matches_scalar():
    values = np.array([0, 5, 10, 50, 90, 95, 100], dtype=float)
    types, severity = classify_series(values, 0, 10, 90, 100)
    expected = [classify_value(v, 0, 10, 90, 100) for v in values]
    assert list(zip(types, severity)) == expected

def test_plant_status():
    assert get_plant_status(0, 0) == "NORMAL"
    assert get_plant_status(4, 0) == "WARNING"
    assert get_plant_status(4, 1) == "CRITICAL"
