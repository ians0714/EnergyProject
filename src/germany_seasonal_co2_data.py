import pandas as pd

INPUT_FILES = r'C:\Users\admin\PycharmProjects\EnergyProject\data\germany-seasonal-co2-v2(by-Notebook-LM).xlsx'

HOUR_LIST = list(range(24))

# =====================================================================
# Carbon Price and Intensity

INPUT_DATA = pd.read_excel(INPUT_FILES, sheet_name='Annual 8760 Profile', header=None)
annual = INPUT_DATA.iloc[4:8764,2:9].copy()
annual.columns = [
    "Timestamp", "Month", "Day", "Hour", "Season", "CO2_Intensity", "Price"
]
annual = annual.set_index("Timestamp")

annual["Price"] = (
    annual["Price"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.strip()
    .astype(float)
)

annual["CO2_Intensity"] = pd.to_numeric(
    annual["CO2_Intensity"]
)

hourly_data = annual[
    (annual["Month"] == 8)
    & (annual["Day"] == 27)
][["Hour", "CO2_Intensity", "Price"]]

monthly_data = (
    annual[annual["Month"] == 8]
    .groupby("Hour")[["CO2_Intensity", "Price"]]
    .mean()
)

seasonal_data = (
    annual[annual["Season"] == "Summer"]
    .groupby("Hour")[["CO2_Intensity", "Price"]]
    .mean()
)

annual_average_data = (
    annual
    .groupby("Hour")[["CO2_Intensity", "Price"]]
    .mean()
)