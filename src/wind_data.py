import pandas as pd

# DATA FILE PATH
WIND_DATA_PATH = (
    r"C:\Users\admin\PycharmProjects\EnergyProject\data\ninja-wind-country-DE-current_onshore-merra2 - 2023.csv"
)

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

wind_data = load_wind_data()

# Set Time as Index
wind_data.set_index("time", inplace=True)