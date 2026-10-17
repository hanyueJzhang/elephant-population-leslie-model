"""Age-structured elephant population models."""

from .leslie_model import (
    DemographicParameters,
    build_leslie_matrix,
    dominant_eigenvalue,
    equilibrium_treatment_fraction,
    simulate,
    synthetic_initial_population,
)
from .treatment_strategy import simulate_repeated_treatment

__all__ = [
    "DemographicParameters",
    "build_leslie_matrix",
    "dominant_eigenvalue",
    "equilibrium_treatment_fraction",
    "simulate",
    "simulate_repeated_treatment",
    "synthetic_initial_population",
]
