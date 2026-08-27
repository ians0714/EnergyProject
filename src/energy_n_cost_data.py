from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_DIR / "data" / "input_data.xlsx"
HOURS_PER_YEAR = 8760

# =========================================================================
# 1. Power Technology Data

INPUT_DATA_ONSITE = pd.read_excel(INPUT_FILE, sheet_name = "onsite-power", header = None)

# Data from Each Energy Source
technologies = INPUT_DATA_ONSITE.iloc[6:12,[1,2,5,6,7]].copy()
technologies.columns = [
    "technology",
    "capacity_mw",
    "LCOE_eur_mwh",
    "additional_cost_eur_mwh",
    "emission_factor_tco2_mwh"
]

# Set Source Name as Index
technologies = technologies.set_index("technology")

# ========================================================================
# 2. Carbon Price

INPUT_DATA_SYSTEM = pd.read_excel(INPUT_FILE, sheet_name = "Sytem-cost", header = None)
carbon_price = INPUT_DATA_SYSTEM.iloc[16,1]
