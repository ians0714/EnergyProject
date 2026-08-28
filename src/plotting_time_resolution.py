import matplotlib.pyplot as plt
from pathlib import Path

from src.modeling_resolution import solve_resolution_dispatch

FIGURE_DIR = Path(__file__).resolve().parent.parent / "figure"
FIGURE_DIR.mkdir(exist_ok=True)

ENERGY_SOURCES = [
    "Wind",
    "Gas turebine",
    "Coal",
    "Nuclear",
    "Biomass",
    "BioCH4-Gas Turebine",
    "Grid"
]


def plot_time_resolution(
    resolution: str,
    selected_carbon_price: float,
    gas_capacity: float,
    coal_capacity: float,
):
    # Solve the Problem First
    result = solve_resolution_dispatch(
        resolution,
        selected_carbon_price,
        gas_capacity,
        coal_capacity,
    )

    # Figure Out which are Active Sources
    active_sources = [
        source
        for source in ENERGY_SOURCES
        if result[source].abs().max() > 1e-6
    ]

    # Prepare Stacked Barplot
    ax = result.set_index("Label")[active_sources].plot(
        kind="bar",
        stacked=True,
        figsize=(12, 6),
        width=0.8,
    )

    # Show Demand
    ax.axhline(
        y=100,
        linestyle="--",
        linewidth=1.5,
        label="Data Center Demand",
    )

    # Title Name
    title_name = {
        "month": "Monthly",
        "season": "Seasonal",
        "year": "Annual",
    }[resolution]

    ax.set_title(f"Data Center Energy Mix - {title_name} Resolution")
    ax.set_xlabel("Time Period")
    ax.set_ylabel("Power Supply (MW)")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))

    plt.xticks(rotation=0)
    plt.tight_layout()
    # Save Figures
    plt.savefig(
        FIGURE_DIR / f"plot_time_resolution_{resolution}.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close()

    return result

# Iterate Plotting
def plot_all_time_resolutions(
    selected_carbon_price: float,
    gas_capacity: float,
    coal_capacity: float,
):
    results = {}

    return results
