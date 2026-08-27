import pandas as pd
from pathlib import Path

# DATA FILE PATH
PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILES = (
    PROJECT_DIR
    / "data"
    / "germany-seasonal-co2-v2(by-Notebook-LM).xlsx"
)

# Load Annual Grid CO2 Intensity and Price Data
INPUT_DATA = pd.read_excel(
    INPUT_FILES,
    sheet_name="Annual 8760 Profile",
    header=None
)

# Select 8760 Hourly Rows and Required Columns
grid_data = INPUT_DATA.iloc[4:8764, 2:9].copy()

# Rename Columns
grid_data.columns = [
    "Timestamp",
    "Month",
    "Day",
    "Hour",
    "Season",
    "CO2_Intensity",
    "Price"
]

# Convert Timestamps to Datetime Format
grid_data["Timestamp"] = pd.to_datetime(
    grid_data["Timestamp"]
)

# Remove the € Sign and Convert Price Data to Float
grid_data["Price"] = (
    grid_data["Price"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.strip()
    .astype(float)
)

# Convert to Numeric Data
grid_data["CO2_Intensity"] = pd.to_numeric(
    grid_data["CO2_Intensity"]
)

# Set Timestamp as Index and Sort Chronologically
grid_data = grid_data.set_index("Timestamp")
grid_data = grid_data.sort_index()