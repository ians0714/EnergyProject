import pandas as pd
from pathlib import Path
from src.modeling import solve_dispatch
from src.plotting import plot_energy_mix

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"

resolutions = ["day", "month", "season", "year"]

def main():
    selected_date = pd.to_datetime(
        input("Select date (2025-MM-DD): ")
    )
    for resolution in resolutions:
        result = solve_dispatch(resolution, selected_date)
        plot_energy_mix(result, resolution)
        print(
            result[
                [
                    "Wind",
                    "Gas turebine",
                    "Coal",
                    "Nuclear",
                    "Biomass",
                    "BioCH4-Gas Turebine",
                    "Grid"
                ]
            ].mean()
        )
        print("BioCH4 sum:",
              result["BioCH4-Gas Turebine"].sum())

        print("BioCH4 max:",
              result["BioCH4-Gas Turebine"].max())

        print("BioCH4 nonzero:",
              (result["BioCH4-Gas Turebine"].abs() > 1e-6).sum())

if __name__ == "__main__":
    main()