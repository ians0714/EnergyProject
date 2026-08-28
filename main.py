import pandas as pd
from pandas.core import col

from src.modeling import solve_dispatch, summarize_dispatch
from src.plotting import plot_energy_mix
from src.energy_n_cost_data import technologies, carbon_price
from src.plotting_time_resolution import plot_time_resolution

horizons = ["day", "month", "season", "year"]

def main():
    # Get Selected Date from User
    selected_date = pd.to_datetime(
        "2025-"+input("Select date (MM-DD): ")
    )

    # Default Value
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

    # No Value then Default Input
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

    # Run Solve for Each Time Horizon
    for horizon in horizons:
        result = solve_dispatch(
            horizon,
            selected_date,
            selected_carbon_price,
            gas_capacity,
            coal_capacity
        )

        summary = summarize_dispatch(
            result,
            horizon,
            selected_carbon_price,
            gas_capacity,
            coal_capacity
        )

        plot_energy_mix(
            result,
            horizon,
            summary
        )

        if horizon != "day":
            # Plot for Each Time Resolution
            plot_time_resolution(
                horizon,
                selected_carbon_price,
                gas_capacity,
                coal_capacity
            )

if __name__ == "__main__":
    main()