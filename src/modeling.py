import pulp

from energy_n_cost_data import technologies, grids, carbon_price
from germany_seasonal_co2_data import seasonal, HOUR_LIST

# Assumption
DATACENTER_DEMAND_MW = 100

# Model
problem = pulp.LpProblem(
    "data_center_dispatch",
    pulp.LpMinimize
)

# Decision variables
# generation[technology, time]
generation = {
    (tech, t): pulp.LpVariable(f"{tech}_{t}", lowBound=0)
    for tech in technologies.index
    for t in HOUR_LIST
}
# grid_import[time]
grid_import = {
    t: pulp.LpVariable(f"grid_{t}", lowBound=0)
    for t in HOUR_LIST
}

# Constraints
# 1. supply == DEMAND_MW
for t in HOUR_LIST:
    problem += (
        pulp.lpSum(generation[tech, t] for tech in technologies.index)
        + grid_import[t]
        == DATACENTER_DEMAND_MW
    )
# 2. generation <= available capacity
for tech in technologies.index:
    for t in HOUR_LIST:
        problem += (
            generation[tech, t]
            <= technologies.loc[tech, "capacity_mw"]
            * technologies.loc[tech, "capacity_factor"]
        )
# Objective
grid_price = seasonal["spring_price"]
grid_carbon_intensity = seasonal["spring_co2"]
problem += pulp.lpSum(
    generation[tech, t]
    * (
        technologies.loc[tech, "LCOE_eur_mwh"]
        + technologies.loc[tech, "additional_cost_eur_mwh"]
        + technologies.loc[tech, "emission_factor_tco2_mwh"] * carbon_price
    )
    for tech in technologies.index
    for t in HOUR_LIST
) + pulp.lpSum(
    grid_import[t]
    * (
        grid_price.loc[t]
        + grid_carbon_intensity.loc[t] * carbon_price
    )
    for t in HOUR_LIST
)
# electricity cost + carbon cost

# Solve
problem.solve(pulp.PULP_CBC_CMD(msg=False))
print(pulp.LpStatus[problem.status])
for t in HOUR_LIST:
    print(f"\nTime: {t}")

    for tech in technologies.index:
        print(
            f"{tech}: {generation[tech, t].value():.2f} MW"
        )

    print(
        f"Grid: {grid_import[t].value():.2f} MW"
    )

print(
    "\nTotal cost:",
    pulp.value(problem.objective)
)