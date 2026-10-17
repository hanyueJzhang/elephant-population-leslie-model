"""Reproduce the main model comparisons and save a portfolio-ready figure."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.leslie_model import (  # noqa: E402
    build_leslie_matrix,
    dominant_eigenvalue,
    equilibrium_treatment_fraction,
    simulate,
    synthetic_initial_population,
)
from src.treatment_strategy import simulate_repeated_treatment  # noqa: E402


def main() -> None:
    years = 200
    initial = synthetic_initial_population()
    equilibrium_fraction = equilibrium_treatment_fraction()

    baseline_matrix = build_leslie_matrix()
    equilibrium_matrix = build_leslie_matrix(treatment_fraction=equilibrium_fraction)
    baseline = simulate(baseline_matrix, initial, years)
    annual_equilibrium = simulate(equilibrium_matrix, initial, years)

    schedules = {}
    for interval in (1, 2, 3):
        trajectory, _ = simulate_repeated_treatment(
            initial,
            years,
            treatment_fraction=equilibrium_fraction,
            effect_duration=2,
            treatment_interval=interval,
        )
        schedules[interval] = trajectory

    print(f"Baseline dominant eigenvalue: {dominant_eigenvalue(baseline_matrix):.6f}")
    print(f"Equilibrium treatment fraction: {equilibrium_fraction:.4%}")
    print(f"Adjusted dominant eigenvalue: {dominant_eigenvalue(equilibrium_matrix):.6f}")
    print(f"Untreated population at year 200: {baseline[-1].sum():,.0f}")

    figure_dir = PROJECT_ROOT / "figures"
    figure_dir.mkdir(exist_ok=True)
    years_axis = range(years + 1)
    plt.figure(figsize=(10, 6))
    plt.plot(years_axis, baseline.sum(axis=1), label="No treatment")
    plt.plot(years_axis, annual_equilibrium.sum(axis=1), label="Constant 20.12% reduction")
    for interval, trajectory in schedules.items():
        plt.plot(
            years_axis,
            trajectory.sum(axis=1),
            label=f"2-year effect, every {interval} year(s)",
            alpha=0.85,
        )
    plt.xlabel("Year")
    plt.ylabel("Modeled population")
    plt.title("Age-structured population scenarios")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    output = figure_dir / "scenario_comparison.png"
    plt.savefig(output, dpi=180)
    print(f"Saved {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
