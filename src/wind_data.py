import pandas as pd
from pathlib import Path

# DATA FILE PATH
PROJECT_DIR = Path(__file__).resolve().parent.parent
WIND_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "ninja-wind-country-DE-current_onshore-merra2 - 2023.csv"
)

# DataFrame with Wind data
def load_wind_data():
    # Read csv File
    df = pd.read_csv(WIND_DATA_PATH)

    # Get wind data
    df = df[["time", "NATIONAL"]].copy()

    # Rename Column
    df = df.rename(
        columns={
            "NATIONAL": "Wind_Capacity_Factor"
        }
    )

    # Time Format Conversion
    df["time"] = pd.to_datetime(
        df["time"],
        utc=True
    )

    # Sort by Time
    df = df.sort_values("time")

    # Index Initialization
    df = df.reset_index(drop=True)

    return df

# Here Comes the Data
wind_data = load_wind_data()

# Set Time as Index
wind_data.set_index("time", inplace=True)