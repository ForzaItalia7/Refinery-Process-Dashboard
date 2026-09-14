"""Central configuration for the Refinery Process Monitoring Dashboard."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "refinery.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

SAMPLING_INTERVAL_MINUTES = 5
DAYS_OF_DATA = 30
RANDOM_SEED = 42

ZSCORE_THRESHOLD = 3.0
ROLLING_WINDOW = 12
ROLLING_THRESHOLD = 3.0
ISOLATION_FOREST_CONTAMINATION = 0.02
MAX_IFOREST_SAMPLES = 5000
STUCK_WINDOW = 12
STUCK_STD_THRESHOLD = 1e-9

APP_TITLE = "Refinery Process Monitoring Dashboard"
APP_ICON = "🏭"
DATA_LABEL = "Synthetic / Simulated Process Data — not connected to any live system"

TIME_RANGES = {
    "Last 1 hour": 1,
    "Last 6 hours": 6,
    "Last 24 hours": 24,
    "Last 7 days": 168,
    "Last 30 days": 720,
}

UNITS = {
    "CDU": {
        "unit_name": "Crude Distillation Unit",
        "unit_type": "Distillation",
        "description": "Primary atmospheric crude oil distillation column",
    },
    "VDU": {
        "unit_name": "Vacuum Distillation Unit",
        "unit_type": "Distillation",
        "description": "Vacuum distillation of atmospheric residue",
    },
    "FCC": {
        "unit_name": "Fluid Catalytic Cracking Unit",
        "unit_type": "Cracking",
        "description": "Catalytic cracking of heavy VGO to lighter products",
    },
    "HDS": {
        "unit_name": "Hydrodesulfurization Unit",
        "unit_type": "Treating",
        "description": "Catalytic removal of sulfur compounds from diesel fraction",
    },
    "NHT": {
        "unit_name": "Naphtha Hydrotreater",
        "unit_type": "Treating",
        "description": "Hydrotreatment of naphtha before reforming",
    },
    "REF": {
        "unit_name": "Catalytic Reformer",
        "unit_type": "Reforming",
        "description": "Catalytic reforming of naphtha to high-octane reformate",
    },
}

# Limits are engineering-style demonstration values, not safety-system setpoints.
PROCESS_VARIABLES = {
    "CDU": [
        {"variable_name": "Furnace Outlet Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 330, "warning_low": 345, "normal_mean": 362, "warning_high": 375, "high_limit": 385, "noise_std": 1.5},
        {"variable_name": "Column Top Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 95, "warning_low": 105, "normal_mean": 120, "warning_high": 135, "high_limit": 148, "noise_std": 1.0},
        {"variable_name": "Column Bottom Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 315, "warning_low": 328, "normal_mean": 340, "warning_high": 352, "high_limit": 362, "noise_std": 1.2},
        {"variable_name": "Column Pressure", "variable_type": "Pressure", "engineering_unit": "bar g", "low_limit": 0.8, "warning_low": 1.0, "normal_mean": 1.5, "warning_high": 1.8, "high_limit": 2.2, "noise_std": 0.03},
        {"variable_name": "Crude Feed Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 160, "warning_low": 175, "normal_mean": 200, "warning_high": 215, "high_limit": 226, "noise_std": 2.0},
        {"variable_name": "Reflux Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 35, "warning_low": 40, "normal_mean": 50, "warning_high": 58, "high_limit": 66, "noise_std": 0.8},
        {"variable_name": "Overhead Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 20, "warning_low": 24, "normal_mean": 30, "warning_high": 34, "high_limit": 39, "noise_std": 0.6},
        {"variable_name": "Bottoms Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 128, "warning_low": 138, "normal_mean": 150, "warning_high": 160, "high_limit": 170, "noise_std": 1.5},
    ],
    "VDU": [
        {"variable_name": "Column Top Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 60, "warning_low": 68, "normal_mean": 80, "warning_high": 95, "high_limit": 106, "noise_std": 1.0},
        {"variable_name": "Column Bottom Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 335, "warning_low": 345, "normal_mean": 358, "warning_high": 370, "high_limit": 382, "noise_std": 1.2},
        {"variable_name": "Column Pressure", "variable_type": "Pressure", "engineering_unit": "mbar abs", "low_limit": 10, "warning_low": 20, "normal_mean": 50, "warning_high": 70, "high_limit": 92, "noise_std": 1.5},
        {"variable_name": "Feed Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 75, "warning_low": 85, "normal_mean": 100, "warning_high": 115, "high_limit": 127, "noise_std": 1.5},
        {"variable_name": "Vacuum Overhead Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 45, "warning_low": 52, "normal_mean": 63, "warning_high": 75, "high_limit": 86, "noise_std": 0.8},
        {"variable_name": "LVGO Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 15, "warning_low": 18, "normal_mean": 24, "warning_high": 30, "high_limit": 36, "noise_std": 0.6},
    ],
    "FCC": [
        {"variable_name": "Reactor Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 445, "warning_low": 460, "normal_mean": 483, "warning_high": 500, "high_limit": 516, "noise_std": 1.8},
        {"variable_name": "Regenerator Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 660, "warning_low": 675, "normal_mean": 700, "warning_high": 720, "high_limit": 736, "noise_std": 2.0},
        {"variable_name": "Reactor Pressure", "variable_type": "Pressure", "engineering_unit": "bar g", "low_limit": 1.2, "warning_low": 1.5, "normal_mean": 1.8, "warning_high": 2.1, "high_limit": 2.5, "noise_std": 0.04},
        {"variable_name": "Feed Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 75, "warning_low": 85, "normal_mean": 100, "warning_high": 115, "high_limit": 127, "noise_std": 1.5},
        {"variable_name": "Catalyst Circulation Rate", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 380, "warning_low": 420, "normal_mean": 500, "warning_high": 570, "high_limit": 625, "noise_std": 6.0},
        {"variable_name": "Main Fractionator Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 305, "warning_low": 320, "normal_mean": 345, "warning_high": 362, "high_limit": 378, "noise_std": 1.5},
        {"variable_name": "Flue Gas Oxygen", "variable_type": "Composition", "engineering_unit": "% vol", "low_limit": 0.5, "warning_low": 1.0, "normal_mean": 2.5, "warning_high": 4.0, "high_limit": 5.5, "noise_std": 0.12},
    ],
    "HDS": [
        {"variable_name": "Reactor Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 310, "warning_low": 325, "normal_mean": 348, "warning_high": 368, "high_limit": 387, "noise_std": 1.2},
        {"variable_name": "Reactor Pressure", "variable_type": "Pressure", "engineering_unit": "bar g", "low_limit": 28, "warning_low": 31, "normal_mean": 35, "warning_high": 38.5, "high_limit": 43, "noise_std": 0.3},
        {"variable_name": "Feed Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 55, "warning_low": 63, "normal_mean": 78, "warning_high": 92, "high_limit": 102, "noise_std": 1.0},
        {"variable_name": "Hydrogen Flow", "variable_type": "Flow", "engineering_unit": "Nm³/h", "low_limit": 1600, "warning_low": 1800, "normal_mean": 2050, "warning_high": 2250, "high_limit": 2420, "noise_std": 25.0},
        {"variable_name": "H2/Feed Ratio", "variable_type": "Ratio", "engineering_unit": "Nm³/t", "low_limit": 18, "warning_low": 21, "normal_mean": 26.3, "warning_high": 30, "high_limit": 34, "noise_std": 0.4},
        {"variable_name": "Product Sulfur Content", "variable_type": "Composition", "engineering_unit": "ppm wt", "low_limit": 0, "warning_low": 0, "normal_mean": 6, "warning_high": 12, "high_limit": 16, "noise_std": 0.5},
    ],
    "NHT": [
        {"variable_name": "Reactor Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 250, "warning_low": 265, "normal_mean": 288, "warning_high": 308, "high_limit": 326, "noise_std": 1.0},
        {"variable_name": "Reactor Pressure", "variable_type": "Pressure", "engineering_unit": "bar g", "low_limit": 23, "warning_low": 26, "normal_mean": 30, "warning_high": 33.5, "high_limit": 38, "noise_std": 0.25},
        {"variable_name": "Feed Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 44, "warning_low": 50, "normal_mean": 60, "warning_high": 68, "high_limit": 76, "noise_std": 0.8},
        {"variable_name": "Hydrogen Flow", "variable_type": "Flow", "engineering_unit": "Nm³/h", "low_limit": 1100, "warning_low": 1250, "normal_mean": 1480, "warning_high": 1680, "high_limit": 1820, "noise_std": 20.0},
        {"variable_name": "Reactor Outlet Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 270, "warning_low": 285, "normal_mean": 308, "warning_high": 328, "high_limit": 347, "noise_std": 1.0},
        {"variable_name": "Stripper Pressure", "variable_type": "Pressure", "engineering_unit": "bar g", "low_limit": 6, "warning_low": 7, "normal_mean": 8.5, "warning_high": 10, "high_limit": 11.8, "noise_std": 0.1},
    ],
    "REF": [
        {"variable_name": "Reactor Inlet Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 455, "warning_low": 468, "normal_mean": 482, "warning_high": 496, "high_limit": 512, "noise_std": 1.2},
        {"variable_name": "Reactor Outlet Temperature", "variable_type": "Temperature", "engineering_unit": "°C", "low_limit": 395, "warning_low": 410, "normal_mean": 428, "warning_high": 445, "high_limit": 462, "noise_std": 1.0},
        {"variable_name": "Reactor Pressure", "variable_type": "Pressure", "engineering_unit": "bar g", "low_limit": 18, "warning_low": 21, "normal_mean": 25, "warning_high": 28.5, "high_limit": 33, "noise_std": 0.2},
        {"variable_name": "Feed Flow", "variable_type": "Flow", "engineering_unit": "t/h", "low_limit": 36, "warning_low": 42, "normal_mean": 50, "warning_high": 57, "high_limit": 64, "noise_std": 0.7},
        {"variable_name": "H2 Production Rate", "variable_type": "Flow", "engineering_unit": "Nm³/h", "low_limit": 1400, "warning_low": 1550, "normal_mean": 1780, "warning_high": 1980, "high_limit": 2120, "noise_std": 25.0},
        {"variable_name": "Research Octane Number", "variable_type": "Quality", "engineering_unit": "RON", "low_limit": 92, "warning_low": 95, "normal_mean": 98, "warning_high": 101, "high_limit": 103.5, "noise_std": 0.3},
        {"variable_name": "Recycle Ratio", "variable_type": "Ratio", "engineering_unit": "mol/mol", "low_limit": 3, "warning_low": 4, "normal_mean": 5.5, "warning_high": 7, "high_limit": 8.2, "noise_std": 0.1},
    ],
}

ABNORMAL_EVENTS = [
    {"unit": "FCC", "variable": "Reactor Temperature", "event_type": "HIGH_SPIKE", "day": 5, "hour": 14, "duration_hours": 2.5, "magnitude": 26.0},
    {"unit": "CDU", "variable": "Crude Feed Flow", "event_type": "LOW_FLOW", "day": 8, "hour": 6, "duration_hours": 3.0, "magnitude": -38.0},
    {"unit": "HDS", "variable": "Reactor Pressure", "event_type": "HIGH_PRESSURE", "day": 12, "hour": 20, "duration_hours": 1.5, "magnitude": 9.0},
    {"unit": "CDU", "variable": "Furnace Outlet Temperature", "event_type": "GRADUAL_DRIFT", "day": 15, "hour": 0, "duration_hours": 48.0, "magnitude": 18.0},
    {"unit": "VDU", "variable": "Column Pressure", "event_type": "SUDDEN_SPIKE", "day": 18, "hour": 10, "duration_hours": 0.5, "magnitude": 42.0},
    {"unit": "FCC", "variable": "Regenerator Temperature", "event_type": "HIGH_SPIKE", "day": 20, "hour": 16, "duration_hours": 3.0, "magnitude": 32.0},
    {"unit": "NHT", "variable": "Reactor Temperature", "event_type": "SENSOR_STUCK", "day": 22, "hour": 8, "duration_hours": 4.0, "magnitude": 0.0},
    {"unit": "HDS", "variable": "Feed Flow", "event_type": "LOW_FLOW", "day": 25, "hour": 4, "duration_hours": 2.0, "magnitude": -28.0},
    {"unit": "REF", "variable": "Reactor Inlet Temperature", "event_type": "HIGH_SPIKE", "day": 27, "hour": 12, "duration_hours": 2.0, "magnitude": 24.0},
]
