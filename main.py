import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"


def main():
    subprocess.run(
        [sys.executable, SRC_DIR / "plotting.py"],
        check=True
    )

    subprocess.run(
        [sys.executable, SRC_DIR / "plotting_cost_heat.py"],
        check=True
    )

    print("All figures have been generated.")


if __name__ == "__main__":
    main()