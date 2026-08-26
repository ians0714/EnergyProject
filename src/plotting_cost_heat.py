from pathlib import Path
import matplotlib.pyplot as plt

FIGURE_DIR = Path(__file__).resolve().parent.parent / "figure"
FIGURE_DIR.mkdir(exist_ok=True)

from energy_n_cost_data import carbon_price
from germany_seasonal_co2_data import annual


# ============================================================
# 1. Prepare data
# ============================================================

data = annual.copy()

# Grid effective cost [€/MWh]
data["Grid_Effective_Cost"] = (
    data["Price"]
    + (data["CO2_Intensity"] / 1000) * carbon_price
)

# 8760 hourly values -> 365 days x 24 hours
heatmap_data = (
    data["Grid_Effective_Cost"]
    .to_numpy()
    .reshape(365, 24)
)


# ============================================================
# 2. Plot
# ============================================================

plt.figure(figsize=(14, 8))

image = plt.imshow(
    heatmap_data,
    aspect="auto",
    origin="lower"
)

plt.colorbar(
    image,
    label="Grid Effective Cost [€/MWh]"
)

plt.title("Annual Hourly Grid Effective Cost")
plt.xlabel("Hour of Day")
plt.ylabel("Day of Year")

plt.xticks(
    range(0, 24, 2)
)

plt.yticks(
    [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 364],
    [1, 31, 61, 91, 121, 151, 181, 211, 241, 271, 301, 331, 365]
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "annual_grid_cost_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()