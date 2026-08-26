# Data Centre Energy Supply Optimization

## 1. Project Question

This project investigates how the electricity demand of a data centre can be supplied using different energy sources while minimizing the total operating cost.

The model compares several electricity supply options, including renewable generation, conventional generation, and electricity from the grid. It also considers the effect of carbon emissions and technology-specific constraints.

The main question is:

**How does the optimal electricity supply mix for a data centre change under different cost, carbon, and technology assumptions?**

The model is designed as a simplified energy system model rather than a detailed representation of an actual data centre or electricity system.

---

## 2. How to Run the Model

The project requires Python and the Python packages used in the source files.

Run the complete model from the project directory with:

```bash
python main.py
```

`main.py` runs the optimization and calls the plotting scripts used to generate the figures.

The generated figures are automatically saved in:

```text
figures/
```

The main Python files are organized by function rather than combining the entire model into one script.

---

## 3. Model Overview

For each time step, the model must satisfy the electricity demand of the data centre.

Electricity can be supplied from the available technologies up to their respective capacity or availability limits. The optimization determines how much electricity should be supplied by each source while minimizing total cost.

The model considers:

* electricity demand
* generation capacity
* technology operating costs
* grid electricity cost
* carbon emissions and carbon cost
* availability or capacity-factor assumptions

The resulting dispatch therefore represents the least-cost solution under the assumptions and constraints included in the model.

---

## 4. Understanding the Results

The main outputs show the amount of electricity supplied by each technology and the associated system cost.

### Electricity supply

Generation or grid supply is expressed in **MW** for each time step.

The sum of electricity supplied by all sources must meet the data centre electricity demand.

### Cost

Technology costs are represented in **EUR/MWh** where applicable.

The optimization uses these costs, together with carbon-related costs and model constraints, to determine the least-cost dispatch.

### Capacity and availability

Installed or available generation capacity is represented in **MW**.

Availability or capacity-factor assumptions limit how much of the nominal capacity can be used during a given time period.

### Carbon emissions

Carbon emission factors describe the emissions associated with electricity generation from each relevant technology. Carbon prices convert these emissions into an additional cost considered by the optimization.

---

## 5. Figures

The figures used for the analysis and presentation are generated directly by the Python scripts.

Running:

```bash
python main.py
```

regenerates the relevant figures and saves them in the `figures/` directory.

This ensures that the figures can be reproduced from the model rather than being manually inserted into the project folder.

---

## 6. Data Sources

*To be added after confirming the original and derived data sources.*

The final version will distinguish between:

* original downloaded data,
* values derived or generated from external data,
* and model assumptions.

---

## 7. Limitations

This is a simplified optimization model intended to explore the behaviour of different electricity supply options.

The results depend on the assumed technology costs, capacities, availability, carbon parameters, and other constraints. They should therefore be interpreted as model results under the selected assumptions rather than as a prediction of the operation of a specific real-world data centre.
