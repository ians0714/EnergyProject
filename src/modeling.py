import pulp
import pandas as pd

from energy_n_cost_data import technologies, grids, carbon_price
from germany_seasonal_co2_data import hourly_data, monthly_data, seasonal_data, annual_average_data, HOUR_LIST
from wind_data import wind_data

# Assumption
DATACENTER_DEMAND_MW = 100

# Dispatch Model
def solve_dispatch(input_data, time_resolution):
    data = input_data.reset_index(drop=True)
    grid_price = data["Price"]
    grid_carbon_intensity = data["CO2_Intensity"] / 1000

    wind_daily = wind_data.loc["2023-08-27"]
    wind_capacity_factor = (
        wind_daily["Wind_Capacity_Factor"]
        .reset_index(drop=True)
    )

    print(f"\n===== {time_resolution} =====")

    for t in HOUR_LIST:
        print(
            t,
            "Price =", grid_price.loc[t],
            "CO2 =", grid_carbon_intensity.loc[t]
        )

    # Effective Technology Costs
    technology_cost = {
        tech : (
            technologies.loc[tech, "LCOE_eur_mwh"]
            + technologies.loc[tech, "additional_cost_eur_mwh"]
            + technologies.loc[tech, "emission_factor_tco2_mwh"]
            * carbon_price
            ) for tech in technologies.index
        }

    # Hourly Effective Grid Cost
    grid_cost = {
        t: (
            grid_price.loc[t]
            + grid_carbon_intensity.loc[t] * carbon_price
        ) for t in HOUR_LIST
    }

    # Model
    problem = pulp.LpProblem(
        f"data_center_dispatch_{time_resolution}",
        pulp.LpMinimize
    )

    # Variables
    generation = {
        (tech, t): pulp.LpVariable(
            f"{time_resolution}_{tech}_{t}",
            lowBound = 0
        ) for tech in technologies.index for t in HOUR_LIST
    }

    grid_import = {
        t : pulp.LpVariable(
            f"{time_resolution}_grid_{t}",
            lowBound=0
        ) for t in HOUR_LIST
    }

    # Constraints
    # 1. Supply = Demand
    for t in HOUR_LIST:
        problem += (
            pulp.lpSum(
                generation[tech, t]
                for tech in technologies.index
            )
            + grid_import[t]
            == DATACENTER_DEMAND_MW
        )
    # 2. Generation Capacity
    for tech in technologies.index:
        for t in HOUR_LIST:
            problem += (
                generation[tech, t]
                <= technologies.loc[tech, "capacity_mw"]
                * technologies.loc[tech, "capacity_factor"]
            )
    # Objective
    problem += (
        pulp.lpSum(
            generation[tech, t] * technology_cost[tech]
            for tech in technologies.index
            for t in HOUR_LIST
        )
        +
        pulp.lpSum(
            grid_import[t] * grid_cost[t]
            for t in HOUR_LIST
        )
    )

    # Solve
    problem.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )
    print(
        time_resolution, ":", pulp.LpStatus[problem.status]
    )

    # Save

    result = pd.DataFrame(index=HOUR_LIST)
    for tech in technologies.index:
        result[tech] = [
            generation[tech, t].value()
            for t in HOUR_LIST
        ]
    result["Grid"] = [
        grid_import[t].value()
        for t in HOUR_LIST
    ]
    result["Grid_Price"] = [
        grid_price.loc[t]
        for t in HOUR_LIST
    ]
    result["Grid_CO2"] = [
        grid_carbon_intensity.loc[t]
        for t in HOUR_LIST
    ]
    result["Grid_Effective_Cost"] = [
        grid_cost[t]
        for t in HOUR_LIST
    ]
    result.index.name = "Hour"
    return result

def summarize_dispatch(result, scenario_name):
    summary = []

    # Onsite technologies
    for tech in technologies.index:
        generation_mwh = result[tech].sum()

        emission_factor = technologies.loc[
            tech, "emission_factor_tco2_mwh"
        ]

        base_cost_per_mwh = (
            technologies.loc[tech, "LCOE_eur_mwh"]
            + technologies.loc[tech, "additional_cost_eur_mwh"]
        )

        carbon_emission = (
            generation_mwh * emission_factor
        )

        energy_cost = (
            generation_mwh * base_cost_per_mwh
        )

        carbon_cost = (
            carbon_emission * carbon_price
        )

        total_cost = (
            energy_cost + carbon_cost
        )

        summary.append({
            "Scenario": scenario_name,
            "Energy_Source": tech,
            "Generation_MWh": generation_mwh,
            "CO2_Emission_t": carbon_emission,
            "Energy_Cost_EUR": energy_cost,
            "Carbon_Cost_EUR": carbon_cost,
            "Total_Cost_EUR": total_cost
        })

    # Grid
    grid_generation = result["Grid"].sum()

    grid_emission = (
        result["Grid"]
        * result["Grid_CO2"]
    ).sum()

    grid_energy_cost = (
        result["Grid"]
        * result["Grid_Price"]
    ).sum()

    grid_carbon_cost = (
        grid_emission * carbon_price
    )

    grid_total_cost = (
        grid_energy_cost + grid_carbon_cost
    )

    summary.append({
        "Scenario": scenario_name,
        "Energy_Source": "Grid",
        "Generation_MWh": grid_generation,
        "CO2_Emission_t": grid_emission,
        "Energy_Cost_EUR": grid_energy_cost,
        "Carbon_Cost_EUR": grid_carbon_cost,
        "Total_Cost_EUR": grid_total_cost
    })

    total_generation = sum(
        row["Generation_MWh"] for row in summary
    )

    total_emission = sum(
        row["CO2_Emission_t"] for row in summary
    )

    total_energy_cost = sum(
        row["Energy_Cost_EUR"] for row in summary
    )

    total_carbon_cost = sum(
        row["Carbon_Cost_EUR"] for row in summary
    )

    total_cost = sum(
        row["Total_Cost_EUR"] for row in summary
    )

    summary.append({
        "Scenario": scenario_name,
        "Energy_Source": "TOTAL",
        "Generation_MWh": total_generation,
        "CO2_Emission_t": total_emission,
        "Energy_Cost_EUR": total_energy_cost,
        "Carbon_Cost_EUR": total_carbon_cost,
        "Total_Cost_EUR": total_cost
    })

    return pd.DataFrame(summary)

# 4 Iterations
hourly_result = solve_dispatch(
    hourly_data,
    "Hourly"
)

monthly_result = solve_dispatch(
    monthly_data,
    "Monthly"
)

seasonal_result = solve_dispatch(
    seasonal_data,
    "Seasonal"
)

annual_result = solve_dispatch(
    annual_average_data,
    "Annual"
)


hourly_summary = summarize_dispatch(
    hourly_result,
    "Hourly"
)

monthly_summary = summarize_dispatch(
    monthly_result,
    "Monthly"
)

seasonal_summary = summarize_dispatch(
    seasonal_result,
    "Seasonal"
)

annual_summary = summarize_dispatch(
    annual_result,
    "Annual"
)

all_summary = pd.concat(
    [
        hourly_summary,
        monthly_summary,
        seasonal_summary,
        annual_summary
    ],
    ignore_index=True
)

print("\n===== Summary =====")
print(all_summary.to_string(index=False))