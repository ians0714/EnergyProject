import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# Figure Directory
# ============================================================

FIGURE_DIR = (
    Path(__file__).resolve().parent.parent
    / "figure"
)

FIGURE_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# Energy Mix Plot
# ============================================================

def plot_energy_mix(
        result,
        resolution
):

    # --------------------------------------------------------
    # 1. Energy Sources
    # --------------------------------------------------------

    energy_sources = [
        "Wind",
        "Gas turebine",
        "Coal",
        "Nuclear",
        "Biomass",
        "BioCH4-Gas Turebine",
        "Grid"
    ]

    # Only plot sources that are actually used
    active_sources = [
        source
        for source in energy_sources
        if result[source].abs().max() > 1e-6
    ]

    print(
        f"{resolution} active sources:",
        active_sources
    )


    # --------------------------------------------------------
    # 2. Figure Size
    # --------------------------------------------------------

    if resolution == "day":
        figure_width = 12

    elif resolution == "month":
        figure_width = 30

    elif resolution == "season":
        figure_width = 60

    elif resolution == "year":
        figure_width = 150

    else:
        figure_width = 12


    # --------------------------------------------------------
    # 3. Plot
    # --------------------------------------------------------

    ax = result[active_sources].plot(
        kind="area",
        stacked=True,
        figsize=(figure_width, 6)
    )


    # --------------------------------------------------------
    # 4. Data Center Demand
    # --------------------------------------------------------

    ax.axhline(
        y=100,
        linestyle="--",
        linewidth=1.5,
        label="Data Center Demand"
    )


    # --------------------------------------------------------
    # 5. Labels
    # --------------------------------------------------------

    ax.set_title(
        f"Data Center Energy Mix - "
        f"{resolution.capitalize()}"
    )

    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Power (MW)"
    )

    ax.set_ylim(
        0,
        105
    )


    # --------------------------------------------------------
    # 6. Legend
    # --------------------------------------------------------

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1)
    )


    # --------------------------------------------------------
    # 7. Grid
    # --------------------------------------------------------

    ax.grid(
        axis="y",
        alpha=0.3
    )


    # --------------------------------------------------------
    # 8. Save
    # --------------------------------------------------------

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"plot_resolution_{resolution}.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()