import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# Figure Directory
# ============================================================

FIGURE_DIR = (
    Path(__file__).resolve().parent.parent
    / "figure"
)

FIGURE_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# Energy Mix Plot
# ============================================================

def plot_energy_mix(
        result,
        resolution,
        summary
):

    # --------------------------------------------------------
    # 1. Energy Sources
    # --------------------------------------------------------

    energy_sources = [
        "Wind",
        "Gas turebine",
        "Coal",
        "Nuclear",
        "Biomass",
        "BioCH4-Gas Turebine",
        "Grid"
    ]

    # Only plot energy sources that are actually used
    active_sources = [
        source
        for source in energy_sources
        if result[source].abs().max() > 1e-6
    ]


    # --------------------------------------------------------
    # 2. Summary Data
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 3. Grid Share
    # --------------------------------------------------------

    grid_share = (
        grid_generation
        / total_generation
        * 100
    )

    # --------------------------------------------------------
    # 4. Display Units
    # --------------------------------------------------------

    if resolution == "day":

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

    # --------------------------------------------------------
    # 5. Information Text
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 6. Figure Size
    # --------------------------------------------------------

    if resolution == "day":
        figure_width = 12

    elif resolution == "month":
        figure_width = 30

    elif resolution == "season":
        figure_width = 60

    elif resolution == "year":
        figure_width = 150

    else:
        figure_width = 12


    # --------------------------------------------------------
    # 7. Energy Mix Plot
    # --------------------------------------------------------

    ax = result[
        active_sources
    ].plot(
        kind="area",
        stacked=True,
        figsize=(figure_width, 6)
    )


    # --------------------------------------------------------
    # 8. Data Center Demand
    # --------------------------------------------------------

    ax.axhline(
        y=100,
        linestyle="--",
        linewidth=1.5,
        label="Data Center Demand"
    )


    # --------------------------------------------------------
    # 9. Title and Axis Labels
    # --------------------------------------------------------

    ax.set_title(
        f"Data Center Energy Mix - "
        f"{resolution.capitalize()}"
    )

    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Power Supply (MW)"
    )

    ax.set_ylim(
        0,
        105
    )


    # --------------------------------------------------------
    # 10. Summary Information
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 11. Legend
    # --------------------------------------------------------

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1)
    )


    # --------------------------------------------------------
    # 12. Grid
    # --------------------------------------------------------

    ax.grid(
        axis="y",
        alpha=0.3
    )


    # --------------------------------------------------------
    # 13. Save Figure
    # --------------------------------------------------------

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"plot_resolution_{resolution}.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()