import pandas as pd
import pulp

from src.energy_n_cost_data import technologies
from src.modeling import prepare_data

DATACENTER_DEMAND_MW = 100

SEASON_ORDER = ["spring", "summer", "fall", "winter"]
SEASON_MONTHS = {
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "fall": [9, 10, 11],
    "winter": [12, 1, 2],
}

hourly_input = prepare_data(pd.Timestamp("2025-01-01"), "year")

def aggregate_inputs(resolution: str) -> pd.DataFrame:
    data = hourly_input.copy()
    data["Timestamp"] = pd.to_datetime(
        "2025-" + data["Time_Key"],
        format="%Y-%m-%d %H:%M"
    )
    if resolution == "month":
        data["Period"] = data["Timestamp"].dt.month
        aggregated = (
            data.groupby("Period", sort=True)
            .agg(
                Price=("Price", "mean"),
                CO2_Intensity=("CO2_Intensity", "mean"),
                Wind_Capacity_Factor=("Wind_Capacity_Factor", "mean"),
                Hours=("Timestamp", "size"),
            )
            .reset_index()
        )
        aggregated["Label"] = pd.to_datetime(
            aggregated["Period"], format="%m"
        ).dt.strftime("%b")

    elif resolution == "season":
        month_to_season = {
            month: season
            for season, months in SEASON_MONTHS.items()
            for month in months
        }
        data["Period"] = data["Timestamp"].dt.month.map(month_to_season)

        aggregated = (
            data.groupby("Period", sort=False)
            .agg(
                Price=("Price", "mean"),
                CO2_Intensity=("CO2_Intensity", "mean"),
                Wind_Capacity_Factor=("Wind_Capacity_Factor", "mean"),
                Hours=("Timestamp", "size"),
            )
            .reindex(SEASON_ORDER)
            .reset_index()
        )
        aggregated["Label"] = aggregated["Period"].str.capitalize()

    elif resolution == "year":
        aggregated = pd.DataFrame(
            {
                "Period": ["year"],
                "Price": [data["Price"].mean()],
                "CO2_Intensity": [data["CO2_Intensity"].mean()],
                "Wind_Capacity_Factor": [data["Wind_Capacity_Factor"].mean()],
                "Hours": [len(data)],
                "Label": ["2025"],
            }
        )

    else:
        raise ValueError("resolution must be 'month', 'season', or 'year'")

    return aggregated

def solve_resolution_dispatch(
    resolution,
    selected_carbon_price,
    gas_capacity,
    coal_capacity,
):

    data = aggregate_inputs(resolution)

    grid_price = data["Price"]
    grid_carbon_intensity = data["CO2_Intensity"] / 1000
    wind_capacity_factor = data["Wind_Capacity_Factor"]
    hours = data["Hours"]

    time_steps = range(len(data))

    # Calculating Costs of Each Technology
    technology_cost = {
        tech: (
            technologies.loc[tech, "LCOE_eur_mwh"]
            + technologies.loc[tech, "additional_cost_eur_mwh"]
            + technologies.loc[tech, "emission_factor_tco2_mwh"]
            * selected_carbon_price
        )
        for tech in technologies.index
    }

    # Cost For Every Hour
    grid_cost = {
        t: grid_price.loc[t]
        + grid_carbon_intensity.loc[t] * selected_carbon_price
        for t in time_steps
    }

    # Optimization Model(Minimize)
    problem = pulp.LpProblem(
        f"data_center_dispatch_{resolution}_resolution",
        pulp.LpMinimize,
    )

    # Decision Variables
    generation = {
        (tech, t): pulp.LpVariable(
            f"{resolution}_{tech}_{t}", lowBound=0
        )
        for tech in technologies.index
        for t in time_steps
    }

    # Importing Electricity from the Offsite Grid
    grid_import = {
        t: pulp.LpVariable(f"{resolution}_grid_{t}", lowBound=0)
        for t in time_steps
    }

    # Constraint 1: Supply = Demand
    for t in time_steps:
        problem += (
            pulp.lpSum(
                generation[tech, t]
                for tech in technologies.index
            )
            + grid_import[t]
            == DATACENTER_DEMAND_MW
        )

    for tech in technologies.index:
        for t in time_steps:
            if tech == "Wind":
                wind_available = (
                    technologies.loc[tech, "capacity_mw"]
                    * wind_capacity_factor.loc[t]
                )
                # Keep the same must-take wind assumption as the existing model.
                problem += generation[tech, t] == min(
                    wind_available, DATACENTER_DEMAND_MW
                )
            elif tech == "Gas turebine":
                problem += generation[tech, t] <= gas_capacity
            elif tech == "Coal":
                problem += generation[tech, t] <= coal_capacity
            else:
                problem += (
                    generation[tech, t]
                    <= technologies.loc[tech, "capacity_mw"]
                )

    # Objective
    problem += (
        pulp.lpSum(
            generation[tech, t] * technology_cost[tech] * hours.loc[t]
            for tech in technologies.index
            for t in time_steps
        )
        + pulp.lpSum(
            grid_import[t] * grid_cost[t] * hours.loc[t]
            for t in time_steps
        )
    )

    # Solve Problem and Check whether Result is Optimal or Not
    problem.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[problem.status]
    print(f"{resolution.capitalize()} resolution status: {status}")
    if status != "Optimal":
        raise RuntimeError(
            f"{resolution} resolution optimization failed: {status}"
        )

    result = pd.DataFrame(index=time_steps)

    # Model Information

    for tech in technologies.index:
        result[tech] = [generation[tech, t].value() for t in time_steps]

    result["Grid"] = [grid_import[t].value() for t in time_steps]
    result["Grid_Price"] = [grid_price.loc[t] for t in time_steps]
    result["Grid_CO2"] = [grid_carbon_intensity.loc[t] for t in time_steps]
    result["Grid_Effective_Cost"] = [grid_cost[t] for t in time_steps]
    result["Wind_CF"] = [wind_capacity_factor.loc[t] for t in time_steps]
    result["Hours"] = [hours.loc[t] for t in time_steps]
    result["Label"] = data["Label"].tolist()

    result.index.name = "Time_Step"
    return result
