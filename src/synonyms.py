"""Common alternative names for devices (used by search, FR-1.1).

Add entries as you find naming differences during testing.
Keys and values are lowercase.
"""
SYNONYMS = {
    "infusion pump": ["infusion system", "pump, infusion"],
    "glucose meter": ["blood glucose monitor", "glucose monitoring system", "glucometer"],
    "pulse oximeter": ["oximeter", "spo2 monitor"],
    "blood pressure monitor": ["sphygmomanometer", "noninvasive blood pressure"],
    "thermometer": ["clinical electronic thermometer", "temperature monitor"],
    "insulin pump": ["insulin infusion pump", "insulin delivery system"],
    "catheter": ["intravascular catheter"],
    "ecg": ["electrocardiograph", "ekg"],
    "x-ray": ["radiographic system", "x-ray system"],
}


def synonyms_for(term):
    """Return known alternative names for a term (may be empty)."""
    return SYNONYMS.get(term.strip().lower(), [])