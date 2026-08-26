import pandas as pd
import numpy as np

INPUT_FILES = r'C:\Users\admin\PycharmProjects\EnergyProject\data\germany-seasonal-co2-v2(by-Notebook-LM).xlsx'

HOUR_LIST = list(range(24))

# =====================================================================
# Carbon Price and Intensity

INPUT_DATA = pd.read_excel(INPUT_FILES, sheet_name='Seasonal 24h Profiles', header=None)
seasonal = INPUT_DATA.iloc[4:28,2:10].copy()
seasonal.columns = [
    "winter_co2",
    "spring_co2",
    "summer_co2",
    "fall_co2",
    "winter_price",
    "spring_price",
    "summer_price",
    "fall_price",
]

seasonal.index = HOUR_LIST
