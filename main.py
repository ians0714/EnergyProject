import pandas as pd
from pathlib import Path
from src.modeling import (
    solve_dispatch,
    summarize_dispatch
)
from src.plotting import plot_energy_mix
from src.energy_n_cost_data import technologies, carbon_price

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"

resolutions = ["day", "month", "season", "year"]

def main():
    selected_date = pd.to_datetime(
        "2025-"+input("Select date (MM-DD): ")
    )
    default_carbon_price = carbon_price
    default_gas_capacity = technologies.loc[
        "Gas turebine", "capacity_mw"
    ]
    default_coal_capacity = technologies.loc[
        "Coal", "capacity_mw"
    ]
    carbon_input = input(
        f"Carbon price [EUR/tCO2] "
        f"(default {default_carbon_price}): "
    )

    gas_input = input(
        f"Gas turbine capacity [MW] "
        f"(default {default_gas_capacity}): "
    )

    coal_input = input(
        f"Coal capacity [MW] "
        f"(default {default_coal_capacity}): "
    )
    selected_carbon_price = (
        float(carbon_input)
        if carbon_input
        else default_carbon_price
    )

    gas_capacity = (
        float(gas_input)
        if gas_input
        else default_gas_capacity
    )

    coal_capacity = (
        float(coal_input)
        if coal_input
        else default_coal_capacity
    )
    for resolution in resolutions:

        result = solve_dispatch(
            resolution,
            selected_date,
            selected_carbon_price,
            gas_capacity,
            coal_capacity
        )

        summary = summarize_dispatch(
            result,
            resolution,
            selected_carbon_price,
            gas_capacity,
            coal_capacity
        )

        plot_energy_mix(
            result,
            resolution,
            summary
        )

if __name__ == "__main__":
    main()