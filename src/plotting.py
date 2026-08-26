# plotting.py
from modeling import (
    hourly_result,
    monthly_result,
    seasonal_result,
    annual_result,
    DATACENTER_DEMAND_MW,
)

from pathlib import Path
import matplotlib.pyplot as plt

FIGURE_DIR = Path(__file__).resolve().parent.parent / "figure"
FIGURE_DIR.mkdir(exist_ok=True)

def plot_dispatch(result, title, filename):

    exclude_columns = [
        "Grid_Price",
        "Grid_CO2",
        "Grid_Effective_Cost",
    ]

    generation_columns = [
        col
        for col in result.columns
        if col not in exclude_columns
    ]

    plt.figure(figsize=(12, 6))

    plt.stackplot(
        result.index,
        *[result[col] for col in generation_columns],
        labels=generation_columns,
    )

    plt.title(title)
    plt.xlabel("Hour of Day")
    plt.ylabel("Power Supply [MW]")

    plt.xlim(0, 23)
    plt.ylim(0, DATACENTER_DEMAND_MW)

    plt.xticks(range(0, 24, 2))

    plt.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.savefig(
        FIGURE_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.tight_layout()
    plt.show()


plot_dispatch(
    hourly_result,
    "Hourly Data Center Power Supply Mix - August 27",
    "hourly_supply_mix.png",
)

plot_dispatch(
    monthly_result,
    "Monthly Average Data Center Power Supply Mix - August",
    "monthly_supply_mix.png",
)

plot_dispatch(
    seasonal_result,
    "Seasonal Average Data Center Power Supply Mix - Summer",
    "seasonal_supply_mix.png",
)

plot_dispatch(
    annual_result,
    "Annual Average Data Center Power Supply Mix",
    "annual_supply_mix.png",
)