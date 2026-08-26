import pulp
import pandas as pd

from energy_n_cost_data import technologies, grids, carbon_price
from germany_seasonal_co2_data import hourly_data, monthly_data, seasonal_data, annual_average_data, HOUR_LIST

# Assumption
DATACENTER_DEMAND_MW = 100

# Dispatch Model
def solve_dispatch(input_data, time_resolution):
    data = input_data.reset_index(drop=True)
    grid_price = data["Price"]
    grid_carbon_intensity = data["CO2_Intensity"] / 1000

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
    # 3. Grid Capacity
    for t in HOUR_LIST:
        problem += (
            grid_import[t]
            <= grids.loc[t, "grid_amount_mwh"] / 365
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

print("\nHourly")
print(hourly_result)

print("\nMonthly")
print(monthly_result)

print("\nSeasonal")
print(seasonal_result)

print("\nAnnual")
print(annual_result)