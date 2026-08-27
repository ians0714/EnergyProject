# AGENTS.md

## 1. Project Objective

This project develops a simplified cost-optimization model for the electricity supply mix of a specific data center.

The objective is to optimize the energy supply mix required to meet the data center's electricity demand and investigate how time-varying input data affect the optimized supply mix and total energy cost.

The base data and optimization time step are **hourly**.

The project has two main forms of analysis.

### 1. Annual Hourly Cost Analysis

Use one year of hourly data to calculate the optimized energy supply mix and total energy cost for each hour.

Visualize the resulting cost in a **365-day × 24-hour heatmap** to investigate temporal variations in energy cost throughout the year.

### 2. Representative 24-Hour Energy Mix Analysis

Create representative 24-hour input profiles from time-varying data, particularly grid electricity price and grid co2 intensity, using four different aggregation periods:

* Annual average
* Seasonal average
* Monthly average
* Daily profile

Optimize the energy supply mix from 00:00 to 23:00 for each profile and compare the resulting 24-hour energy mixes.

---

## 2. Model Scope

### Data Center Demand

The default data center electricity demand is fixed at **100 MW**.

The demand parameter may be changed when explicitly requested, but the current model does not use a time-varying demand profile.

The same demand is therefore applied to every modeled hour.

### Onsite Energy Sources

The following technologies are treated as onsite energy sources:

* Wind
* Gas turbine
* Coal
* Biomass
* Bio-CH4 gas turbine

### Offsite Energy Source

Electricity supplied from the external grid is treated as an **offsite energy source**.

Both onsite generation and offsite grid electricity are considered supply options in the optimization.

Do not treat grid electricity as a residual or backup source. Do not assume a priority order between onsite generation and offsite grid electricity unless explicitly specified.

Their contributions to the optimized energy mix are determined by their costs, carbon costs, capacities, and other constraints defined in the model.

### Waste Heat

Waste heat is outside the scope of the current model.

---

## 3. Time Data and Representative 24-Hour Profiles

The base dataset consists of **one year of hourly data**.

The underlying optimization time structure is also hourly.

The project investigates how the aggregation period used for time-varying inputs affects the resulting 24-hour energy supply mix.

The 24-hour structure always remains **00:00–23:00**. The difference between the cases is the period used to calculate the representative input value for each hour of the day.

### 1. Annual Average Profile

For each hour of the day, calculate the average of the corresponding hourly observations across the entire year.

For example:

* 00:00 = average of all 00:00 observations in the annual dataset
* 01:00 = average of all 01:00 observations
* ...
* 23:00 = average of all 23:00 observations

This produces a representative annual 24-hour input profile.

### 2. Seasonal Average Profile

The current seasonal case represents **summer: June, July, and August**.

For each hour of the day, calculate the average using observations from the selected season.

### 3. Monthly Average Profile

The current monthly case represents **August**.

For each hour of the day, calculate the average using observations from August.

### 4. Daily Profile

The current daily case represents **August 27**.

Use the actual hourly input values from 00:00 to 23:00 without averaging across multiple days.

### Important Interpretation

Annual, seasonal, monthly, and daily cases do **not** represent different optimization time-step lengths.

The underlying structure remains **hourly**.

The difference is the **aggregation period used to construct the representative 24-hour time-varying input profile**.

---

## 4. Input Data

### Data Center Demand

* Default: 100 MW
* Constant over time
* May be changed as a model parameter when explicitly requested

### Wind

Use hourly wind availability or capacity-factor data.

Wind generation must not exceed the available wind generation for each hour.

### Other Onsite Technologies

Use the parameters defined in the current project inputs/model, including where applicable:

* Capacity
* Generation cost
* Emission factor

### Grid

Use the grid inputs defined in the project, including where applicable:

* Grid electricity cost
* Grid-related emission data
* Other grid parameters already defined in the model

Where hourly grid cost data are available, preserve their hourly variation.

For representative 24-hour analyses, process the hourly grid cost according to the annual, seasonal, monthly, or daily profile definition described above.

### Data Rules

The actual project code and input data are the source of truth for numerical parameter values and units.

Unless explicitly instructed:

* Do not modify input values.
* Do not invent missing data.
* Do not replace real input data with synthetic data.

If required information is missing, report it instead of silently introducing an assumption.

---

## 5. Optimization Model

Use **PuLP** for optimization.

### Objective Function

The primary objective is to minimize the **total energy supply cost** while satisfying the data center electricity demand.

The objective includes, according to the formulation defined in the current model:

* Energy generation / electricity supply cost
* Carbon cost

Calculate carbon emissions using the emission factors associated with the energy sources and include carbon cost using the defined carbon price.

### Energy Balance

For every modeled hour, the combined onsite and offsite electricity supply must satisfy the data center electricity demand.

### Capacity Constraints

Generation from each technology must not exceed its defined capacity.

### Wind Availability Constraint

Hourly wind generation must not exceed the amount available according to the hourly wind availability or capacity factor.

### Additional Constraints

Add policy, emissions, or operational constraints only when explicitly agreed upon and requested.

Do not independently introduce new constraints.

---

## 6. Analysis and Sensitivity

The project may analyze how changes in selected model parameters affect:

* Total cost
* Energy generation mix
* Carbon emissions

Use sensitivity variables and parameter ranges defined in the current project or explicitly agreed upon by the project team.

Do not introduce new scenarios or parameter variations solely to make the results more interesting.

---

## 7. Outputs and Visualization

The main outputs are divided into two categories.

### A. Annual Cost Heatmap

Use the annual hourly input data to perform the required optimization for each hour.

Visualize the resulting total energy cost as a heatmap:

* X-axis: Hour of day (0–23)
* Y-axis: Day of year (1–365)
* Value: Estimated total energy cost for that hour

The purpose is to observe how optimized energy cost varies by hour and date throughout the year.

### B. Representative 24-Hour Energy Mix Charts

Calculate optimized energy mixes for four representative 24-hour input profiles.

#### Annual Average

Average the relevant time-varying inputs for each hour of the day across the entire annual dataset and calculate the resulting 24-hour energy mix.

#### Summer Average

Average the relevant inputs for each hour of the day using June, July, and August data.

#### August Average

Average the relevant inputs for each hour of the day using August data.

#### August 27

Use the actual hourly input data for August 27.

### Plotting Rules

* Display energy mixes as stacked charts.
* Make individual energy sources visually distinguishable.
* Use consistent colors for the same energy source across all four energy-mix charts.
* A varied and clearly distinguishable color palette may be used.
* Use 00:00–23:00 on the x-axis.
* Clearly label axes and units.
* Keep formatting and design consistent across the four energy-mix plots.
* Plotting code must not alter the underlying optimization results.

---

## 8. Project Structure

Respect the existing project structure and separation of responsibilities:

```text id="mpajdm"
project/
│
├── main.py
├── AGENTS.md
├── readme.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── input_data.xlsx
│   ├── germany-seasonal-co2-v2(by-Notebook-LM).xlsx
│   └── reference.txt
│
├── figure/
│
└── src/
    ├── energy_n_cost_data.py
    ├── germany_seasonal_co2_data.py
    ├── modeling.py
    ├── plotting.py
    └── plotting_cost_heat.py
```

### `main.py`

Main executable entry point.

Coordinate the existing data-processing, optimization, and plotting modules.

Keep detailed data-processing and optimization logic in their respective modules rather than moving it into `main.py`.

### `src/energy_n_cost_data.py`

Load the main model parameters from `data/input_data.xlsx` using pandas.

This module currently processes:

* Onsite power technology data
* Technology capacity
* Capacity factor
* LCOE
* Additional generation cost
* Technology emission factors
* Grid-related input data
* Carbon price

Treat the Excel input file as the source of truth for these numerical parameters.

Do not duplicate these numerical values directly in the model code when they are already available from the input file.

### `src/germany_seasonal_co2_data.py`

Load and process the annual 8760-hour grid dataset from:

`data/germany-seasonal-co2-v2(by-Notebook-LM).xlsx`

This module processes the time-varying:

* Grid electricity price
* Grid CO2 intensity

It also constructs the four representative 24-hour profiles used by the project:

* Annual average profile
* Summer average profile
* August average profile
* August 27 daily profile

For annual, seasonal, and monthly profiles, preserve the existing hour-of-day aggregation logic. Values for each hour should be calculated from observations corresponding to the same hour of day.

The August 27 profile should use the actual hourly observations for that day rather than averages across multiple days.

Do not change the aggregation methodology unless explicitly requested.

### `src/modeling.py`

Implement the energy supply cost optimization using PuLP.

This module should contain the optimization logic, including where applicable:

* Decision variables
* Energy balance
* Capacity constraints
* Wind availability constraints
* Electricity supply cost
* Carbon cost
* Other explicitly agreed constraints

Use the processed inputs from the data modules rather than independently redefining input values.

Do not introduce an unspecified priority between onsite generation and offsite grid electricity.

### `src/plotting.py`

Generate the representative 24-hour energy-mix visualizations from optimization results.

The current comparison consists of:

* Annual average profile
* Summer average profile
* August average profile
* August 27 profile

Keep technology representation, colors, axes, units, and general formatting consistent across the four charts.

### `src/plotting_cost_heat.py`

Generate the annual hourly optimized energy-cost heatmap using the annual hourly analysis.

The intended heatmap structure is:

* X-axis: Hour of day (0–23)
* Y-axis: Day of year
* Value: Estimated optimized total energy cost

Keep heatmap generation separate from optimization logic.

### `data/`

Store the source datasets used by the project.

The current input files include the main technology/system input workbook and the annual hourly grid price/CO2 dataset.

Do not modify source datasets or replace them with generated data unless explicitly requested.

### `data/reference.txt`

Maintain information about the sources and references for the project datasets.

Do not remove existing source information when modifying data-related code.

### `figure/`

Store generated figures and heatmaps.

### `requirements.txt`

Maintain the Python dependencies required to run the project.

Avoid adding unnecessary dependencies when the task can be completed using the existing project dependencies.

### `readme.md`

Provide the human-readable project overview and instructions for running the model.

### `AGENTS.md`

Provide project context, modeling assumptions, code-structure information, and development rules for coding agents.

---

## 9. Coding Agent Rules

The coding agent is an **implementation and development assistant**. Major modeling decisions remain human decisions.

When working on this repository:

1. Inspect the existing project structure and relevant code before making changes.
2. Do not change established modeling assumptions unless explicitly instructed.
3. Do not independently change input data, energy sources, the objective function, or constraints.
4. Do not invent missing data.
5. If required information is missing, report it rather than silently introducing assumptions.
6. Preserve working existing code where possible and make only the changes necessary for the requested task.
7. Prefer clear Python code that students can read, understand, and explain.
8. Avoid unnecessary classes, abstractions, frameworks, and dependencies.
9. Keep data processing, optimization, and plotting responsibilities separated where practical.
10. After modifying optimization code, verify demand balance, capacity constraints, wind availability, and solver status where practical.
11. When modifying cost or carbon calculations, verify unit consistency.
12. Plotting code must not modify the underlying optimization results.
13. After making changes, summarize which files and functionality were modified.
14. If a request requires an ambiguous modeling decision, ask for clarification rather than silently choosing an assumption.
15. Do not introduce an unspecified priority rule between onsite generation and offsite grid electricity.

---

## 10. General Development Principles

This project is not intended to become an unnecessarily complex energy-system model.

The goal is to maintain a simplified optimization model that is:

* Transparent
* Explainable
* Reproducible
* Physically meaningful

Do not increase model complexity without a clear and explicitly requested analytical purpose.

A model is not considered correct merely because the Python code executes successfully.

When modifying the project, preserve:

* Physical interpretation
* Mathematical consistency
* Unit consistency
* Reproducibility
* Code readability
