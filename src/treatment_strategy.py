"""Deterministic simulations of repeated, finite-duration fertility treatment."""

import numpy as np

from .leslie_model import DemographicParameters, build_leslie_matrix


def active_treatment_fraction(
    year: int,
    treatment_fraction: float,
    effect_duration: int,
    treatment_interval: int,
) -> float:
    """Combine independent active treatment cohorts in a given year.

    If more than one treatment event is still active, the untreated shares multiply.
    This is a transparent cohort approximation, not an individual-level clinical model.
    """

    active_events = sum(
        1
        for event_year in range(0, year + 1, treatment_interval)
        if year - event_year < effect_duration
    )
    return 1.0 - (1.0 - treatment_fraction) ** active_events


def simulate_repeated_treatment(
    initial_population: np.ndarray,
    years: int,
    treatment_fraction: float,
    effect_duration: int,
    treatment_interval: int,
    params: DemographicParameters = DemographicParameters(),
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate scheduled fertility treatment and return trajectory and yearly coverage."""

    if years < 0:
        raise ValueError("years must be non-negative")
    if not 0.0 <= treatment_fraction <= 1.0:
        raise ValueError("treatment_fraction must be between 0 and 1")
    if effect_duration < 1 or treatment_interval < 1:
        raise ValueError("duration and interval must be positive integers")

    initial = np.asarray(initial_population, dtype=float)
    if initial.size != params.age_classes or np.any(initial < 0):
        raise ValueError("initial_population must be a non-negative 71-class vector")

    trajectory = np.empty((years + 1, params.age_classes), dtype=float)
    coverage = np.empty(years, dtype=float)
    trajectory[0] = initial

    for year in range(years):
        coverage[year] = active_treatment_fraction(
            year, treatment_fraction, effect_duration, treatment_interval
        )
        matrix = build_leslie_matrix(params, coverage[year])
        trajectory[year + 1] = matrix @ trajectory[year]
    return trajectory, coverage
