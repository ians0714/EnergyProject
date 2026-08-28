import matplotlib.pyplot as plt
from pathlib import Path

from src.modeling_resolution import solve_resolution_dispatch
from src.energy_n_cost_data import technologies

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

    total_generation = sum(
        (
            result[source]
            * result["Hours"]
        ).sum()
        for source in ENERGY_SOURCES
    )

    grid_generation = (
        result["Grid"]
        * result["Hours"]
    ).sum()

    grid_share = (
        grid_generation
        / total_generation
        * 100
    )

    total_co2 = 0
    total_cost = 0

    for tech in technologies.index:
        generation_mwh = (
            result[tech]
            * result["Hours"]
        ).sum()

        emission_factor = technologies.loc[
            tech,
            "emission_factor_tco2_mwh"
        ]

        base_cost_per_mwh = (
            technologies.loc[
                tech,
                "LCOE_eur_mwh"
            ]
            + technologies.loc[
                tech,
                "additional_cost_eur_mwh"
            ]
        )

        carbon_emission = (
            generation_mwh
            * emission_factor
        )

        energy_cost = (
            generation_mwh
            * base_cost_per_mwh
        )

        carbon_cost = (
            carbon_emission
            * selected_carbon_price
        )

        total_co2 += carbon_emission
        total_cost += (
            energy_cost
            + carbon_cost
        )

    grid_emission = (
        result["Grid"]
        * result["Grid_CO2"]
        * result["Hours"]
    ).sum()

    grid_energy_cost = (
        result["Grid"]
        * result["Grid_Price"]
        * result["Hours"]
    ).sum()

    grid_carbon_cost = (
        grid_emission
        * selected_carbon_price
    )

    total_co2 += grid_emission
    total_cost += (
        grid_energy_cost
        + grid_carbon_cost
    )

    generation_value = (
        total_generation / 1000
    )
    generation_unit = "GWh"

    cost_value = total_cost
    cost_unit = "EUR"

    co2_value = total_co2
    co2_unit = "tCO2"

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
