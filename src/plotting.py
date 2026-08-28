import matplotlib.pyplot as plt
from pathlib import Path

# Figure Directory
FIGURE_DIR = (Path(__file__).resolve().parent.parent / "figure")
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

# Plot Function for Energy Mix
def plot_energy_mix(
        result,
        horizon,
        summary
):

    # Only plot energy sources that are actually used
    active_sources = [
        source
        for source in ENERGY_SOURCES
        if result[source].abs().max() > 1e-6
    ]

    # Summary for InfoText
    total_row = summary[
        summary["Energy_Source"] == "TOTAL"
    ].iloc[0]
    grid_row = summary[
        summary["Energy_Source"] == "Grid"
    ].iloc[0]
    total_generation = (
        total_row["Generation_MWh"]
    )
    total_co2 = (
        total_row["CO2_Emission_t"]
    )
    total_cost = (
        total_row["Total_Cost_EUR"]
    )
    grid_generation = (
        grid_row["Generation_MWh"]
    )

    # Grid Share
    grid_share = (
        grid_generation
        / total_generation
        * 100
    )

    # Display Units
    # Total Generation
    # The Total Electricity Supplied During the
    # Selected Period. It is Displayed in MWh
    # for Daily Results and GWh for Longer Tme Horizons.
    if horizon == "day":
        generation_value = total_generation
        generation_unit = "MWh"

    else:
        generation_value = (
                total_generation / 1000
        )
        generation_unit = "GWh"

    cost_value = total_cost
    cost_unit = "EUR"

    co2_value = total_co2
    co2_unit = "tCO2"

    # InfoText
    info_text = (
        f"Total Generation: "
        f"{generation_value:.1f} {generation_unit}\n"
        f"Total Cost: "
        f"{cost_value:.2f} {cost_unit}\n"
        f"Total CO2: "
        f"{co2_value:.2f} {co2_unit}\n"
        f"Grid Share: "
        f"{grid_share:.1f}%"
    )

    # Set Figure Size to Make Energy Source Colors Easier to Distinguish
    if horizon == "day":
        figure_width = 12
    elif horizon == "month":
        figure_width = 30
    elif horizon == "season":
        figure_width = 60
    elif horizon == "year":
        figure_width = 150
    else:
        figure_width = 12

    # Plot the Graph!
    ax = result[
        active_sources # Just Plot Active Sources Only
    ].plot(
        kind="area",
        stacked=True,
        figsize=(figure_width, 6)
    ) # Stacked Plot

    # Show Demand
    ax.axhline(
        y=100,
        linestyle="--",
        linewidth=1.5,
        label="Data Center Demand"
    )

    # Title and Labels
    ax.set_title(
        f"Data Center Energy Mix - "
        f"{horizon.capitalize()}"
    )
    ax.set_xlabel(
        "Time (H)"
    )
    ax.set_ylabel(
        "Power Supply (MW)"
    )
    ax.set_ylim(
        0,
        105
    )

    # InfoText Style
    ax.text(
        1.01,
        0.65,
        info_text,
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=10,
        bbox={
            "boxstyle": "round",
            "alpha": 0.1
        }
    )

    # Legend
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1)
    )

    # Grid
    ax.grid(
        axis="y",
        alpha=0.3
    )

    # Save the Plot
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR
        / f"plot_horizon_{horizon}.png",
        dpi=200,
        bbox_inches="tight"
    )
    plt.close()