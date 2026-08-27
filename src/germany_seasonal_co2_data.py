import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILES = (
    PROJECT_DIR
    / "data"
    / "germany-seasonal-co2-v2(by-Notebook-LM).xlsx"
)

INPUT_DATA = pd.read_excel(
    INPUT_FILES,
    sheet_name="Annual 8760 Profile",
    header=None
)

grid_data = INPUT_DATA.iloc[4:8764, 2:9].copy()

grid_data.columns = [
    "Timestamp",
    "Month",
    "Day",
    "Hour",
    "Season",
    "CO2_Intensity",
    "Price"
]

grid_data["Timestamp"] = pd.to_datetime(
    grid_data["Timestamp"]
)

grid_data["Price"] = (
    grid_data["Price"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.strip()
    .astype(float)
)

grid_data["CO2_Intensity"] = pd.to_numeric(
    grid_data["CO2_Intensity"]
)

grid_data = grid_data.set_index("Timestamp")
grid_data = grid_data.sort_index()