import pulp
import pandas as pd

from src.energy_n_cost_data import technologies, carbon_price
from src.germany_seasonal_co2_data import grid_data
from src.wind_data import wind_data

# ============================================================
# Assumptions
# ============================================================

DATACENTER_DEMAND_MW = 100
SELECTED_DATE = "2023-08-27"

SEASON_MONTHS = {
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "fall": [9, 10, 11],
    "winter": [12, 1, 2]
}

resolutions = ["day", "month", "season", "year"]

# Prepare for Time Resolution
def prepare_data(date, resolution):
    month = date.month

    if resolution == resolutions[0]:
        day = date.day
        grid_selected = grid_data[(grid_data.index.month == month) & (grid_data.index.day == day)].copy()
        wind_selected = wind_data[(wind_data.index.month == month) & (wind_data.index.day == day)].copy()
    elif resolution == resolutions[1]:
        grid_selected = grid_data[(grid_data.index.month == month)].copy()
        wind_selected = wind_data[(wind_data.index.month == month)].copy()
    elif resolution == resolutions[2]:
        season = (
            "spring" if month in [3, 4, 5]
            else "summer" if month in [6, 7, 8]
            else "fall" if month in [9, 10, 11]
            else "winter"
        )

        season_date = SEASON_MONTHS[season]

        grid_selected = grid_data[
            grid_data.index.month.isin(season_date)
        ].copy()

        wind_selected = wind_data[
            wind_data.index.month.isin(season_date)
        ].copy()

    elif resolution == resolutions[3]:
        grid_selected = grid_data.copy()
        wind_selected = wind_data.copy()

    else:
        raise ValueError(
            "resolution must be day, month, season, or year"
        )

    grid_selected["Time_Key"] = (
        grid_selected.index.strftime("%m-%d %H:%M")
    )

    wind_selected["Time_Key"] = (
        wind_selected.index.strftime("%m-%d %H:%M")
    )

    grid_wind_selected = pd.merge(grid_selected,
    wind_selected[["Wind_Capacity_Factor", "Time_Key"]],
    on="Time_Key")

    grid_wind_selected = (
        grid_wind_selected
        .sort_values("Time_Key")
        .reset_index(drop=True)
    )

    return grid_wind_selected

# ============================================================
# Dispatch Model
# ============================================================

def solve_dispatch(time_resolution, selected_date):

    # --------------------------------------------------------
    # 1. Input data
    # --------------------------------------------------------

    data = prepare_data(selected_date, time_resolution)

    grid_price = data["Price"]

    grid_carbon_intensity = (
        data["CO2_Intensity"] / 1000
    )

    wind_capacity_factor = (
        data["Wind_Capacity_Factor"]
    )

    time_steps = range(len(data))

    # --------------------------------------------------------
    # 3. Effective Technology Costs
    # --------------------------------------------------------

    technology_cost = {
        tech: (
            technologies.loc[tech, "LCOE_eur_mwh"]
            + technologies.loc[
                tech,
                "additional_cost_eur_mwh"
            ]
            + technologies.loc[
                tech,
                "emission_factor_tco2_mwh"
            ] * carbon_price
        )
        for tech in technologies.index
    }

    # --------------------------------------------------------
    # 4. Hourly Effective Grid Cost
    # --------------------------------------------------------

    grid_cost = {
        t: (
            grid_price.loc[t]
            + grid_carbon_intensity.loc[t]
            * carbon_price
        )
        for t in time_steps
    }

    # --------------------------------------------------------
    # 5. Optimization Model
    # --------------------------------------------------------

    problem = pulp.LpProblem(
        f"data_center_dispatch_{time_resolution}",
        pulp.LpMinimize
    )

    # --------------------------------------------------------
    # 6. Decision Variables
    # --------------------------------------------------------

    generation = {
        (tech, t): pulp.LpVariable(
            f"{time_resolution}_{tech}_{t}",
            lowBound=0
        )
        for tech in technologies.index
        for t in time_steps
    }

    grid_import = {
        t: pulp.LpVariable(
            f"{time_resolution}_grid_{t}",
            lowBound=0
        )
        for t in time_steps
    }

    # --------------------------------------------------------
    # 7. Constraint 1: Supply = Demand
    # --------------------------------------------------------

    for t in time_steps:

        problem += (
            pulp.lpSum(
                generation[tech, t]
                for tech in technologies.index
            )
            + grid_import[t]
            == DATACENTER_DEMAND_MW
        )

    # --------------------------------------------------------
    # 8. Constraint 2: Generation Capacity
    # --------------------------------------------------------

    for tech in technologies.index:

        for t in time_steps:

            # Wind:
            # Must-take generation based on hourly Wind CF
            if tech == "Wind":

                wind_available = (
                    technologies.loc[
                        tech,
                        "capacity_mw"
                    ]
                    * wind_capacity_factor.loc[t]
                )

                problem += (
                    generation[tech, t]
                    == min(
                        wind_available,
                        DATACENTER_DEMAND_MW
                    ) # If Energy Generated Over Demand, Surplus Curtailed
                )

            # Other onsite technologies:
            # No input Capacity Factor
            else:

                problem += (
                    generation[tech, t]
                    <= technologies.loc[
                        tech,
                        "capacity_mw"
                    ]
                )

    # --------------------------------------------------------
    # 9. Objective Function
    # --------------------------------------------------------

    problem += (
        pulp.lpSum(
            generation[tech, t]
            * technology_cost[tech]
            for tech in technologies.index
            for t in time_steps
        )
        +
        pulp.lpSum(
            grid_import[t]
            * grid_cost[t]
            for t in time_steps
        )
    )

    # --------------------------------------------------------
    # 10. Solve
    # --------------------------------------------------------

    problem.solve(
        pulp.PULP_CBC_CMD(
            msg=False
        )
    )

    print(
        "\nOptimization status:",
        pulp.LpStatus[problem.status]
    )

    # --------------------------------------------------------
    # 11. Save Results
    # --------------------------------------------------------

    result = pd.DataFrame(
        index=time_steps
    )

    for tech in technologies.index:
        result[tech] = [
            generation[tech, t].value()
            for t in time_steps
        ]

    result["Grid"] = [
        grid_import[t].value()
        for t in time_steps
    ]

    result["Grid_Price"] = [
        grid_price.loc[t]
        for t in time_steps
    ]

    result["Grid_CO2"] = [
        grid_carbon_intensity.loc[t]
        for t in time_steps
    ]

    result["Grid_Effective_Cost"] = [
        grid_cost[t]
        for t in time_steps
    ]

    result["Wind_CF"] = [
        wind_capacity_factor.loc[t]
        for t in time_steps
    ]

    result["Wind_Available"] = [
        technologies.loc["Wind", "capacity_mw"]
        * wind_capacity_factor.loc[t]
        for t in time_steps
    ]

    result["Time"] = [
        data.loc[t, "Time_Key"]
        for t in time_steps
    ]

    result.index.name = "Time_Step"

    return result

# ============================================================
# Summary
# ============================================================

def summarize_dispatch(
        result,
        scenario_name
):

    summary = []

    number_of_hours = len(result)

    # --------------------------------------------------------
    # 1. Onsite Technologies
    # --------------------------------------------------------

    for tech in technologies.index:

        generation_mwh = (
            result[tech].sum()
        )

        installed_capacity = (
            technologies.loc[
                tech,
                "capacity_mw"
            ]
        )

        emission_factor = (
            technologies.loc[
                tech,
                "emission_factor_tco2_mwh"
            ]
        )

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

        # CO2 emissions
        carbon_emission = (
            generation_mwh
            * emission_factor
        )

        # Energy cost
        energy_cost = (
            generation_mwh
            * base_cost_per_mwh
        )

        # Carbon cost
        carbon_cost = (
            carbon_emission
            * carbon_price
        )

        # Total cost
        total_cost = (
            energy_cost
            + carbon_cost
        )

        # --------------------------------------------
        # Capacity Factor / Utilization
        # --------------------------------------------

        if installed_capacity > 0:

            calculated_cf = (
                generation_mwh
                /
                (
                    installed_capacity
                    * number_of_hours
                )
            )

        else:

            calculated_cf = 0

        summary.append({
            "Scenario": scenario_name,
            "Energy_Source": tech,
            "Installed_Capacity_MW":
                installed_capacity,
            "Generation_MWh":
                generation_mwh,
            "Calculated_CF_Percent":
                calculated_cf * 100,
            "CO2_Emission_t":
                carbon_emission,
            "Energy_Cost_EUR":
                energy_cost,
            "Carbon_Cost_EUR":
                carbon_cost,
            "Total_Cost_EUR":
                total_cost
        })

    # --------------------------------------------------------
    # 2. Grid
    # --------------------------------------------------------

    grid_generation = (
        result["Grid"].sum()
    )

    grid_emission = (
        result["Grid"]
        * result["Grid_CO2"]
    ).sum()

    grid_energy_cost = (
        result["Grid"]
        * result["Grid_Price"]
    ).sum()

    grid_carbon_cost = (
        grid_emission
        * carbon_price
    )

    grid_total_cost = (
        grid_energy_cost
        + grid_carbon_cost
    )

    summary.append({
        "Scenario": scenario_name,
        "Energy_Source": "Grid",
        "Installed_Capacity_MW": None,
        "Generation_MWh":
            grid_generation,
        "Calculated_CF_Percent": None,
        "CO2_Emission_t":
            grid_emission,
        "Energy_Cost_EUR":
            grid_energy_cost,
        "Carbon_Cost_EUR":
            grid_carbon_cost,
        "Total_Cost_EUR":
            grid_total_cost
    })

    # --------------------------------------------------------
    # 3. Total
    # --------------------------------------------------------

    total_generation = sum(
        row["Generation_MWh"]
        for row in summary
    )

    total_emission = sum(
        row["CO2_Emission_t"]
        for row in summary
    )

    total_energy_cost = sum(
        row["Energy_Cost_EUR"]
        for row in summary
    )

    total_carbon_cost = sum(
        row["Carbon_Cost_EUR"]
        for row in summary
    )

    total_cost = sum(
        row["Total_Cost_EUR"]
        for row in summary
    )

    summary.append({
        "Scenario": scenario_name,
        "Energy_Source": "TOTAL",
        "Installed_Capacity_MW": None,
        "Generation_MWh":
            total_generation,
        "Calculated_CF_Percent": None,
        "CO2_Emission_t":
            total_emission,
        "Energy_Cost_EUR":
            total_energy_cost,
        "Carbon_Cost_EUR":
            total_carbon_cost,
        "Total_Cost_EUR":
            total_cost
    })

    return pd.DataFrame(summary)