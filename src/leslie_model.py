"""Core Leslie-matrix utilities for an age-structured elephant model."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DemographicParameters:
    """Parameters used to construct the 71-class annual projection matrix."""

    maximum_age: int = 70
    reproductive_start_age: int = 10
    reproductive_end_age: int = 60
    birth_interval_years: float = 3.5
    female_birth_fraction: float = 0.5
    calf_survival: float = 0.75
    adult_survival: float = 0.95
    senescent_decay: float = 1.106

    @property
    def age_classes(self) -> int:
        return self.maximum_age + 1

    @property
    def annual_female_fertility(self) -> float:
        return self.female_birth_fraction / self.birth_interval_years


def fertility_vector(
    params: DemographicParameters = DemographicParameters(),
    treatment_fraction: float = 0.0,
) -> np.ndarray:
    """Return age-specific fertility after a proportional fertility reduction."""

    if not 0.0 <= treatment_fraction <= 1.0:
        raise ValueError("treatment_fraction must be between 0 and 1")

    fertility = np.zeros(params.age_classes, dtype=float)
    fertile = slice(params.reproductive_start_age, params.reproductive_end_age + 1)
    fertility[fertile] = params.annual_female_fertility * (1.0 - treatment_fraction)
    return fertility


def survival_vector(params: DemographicParameters = DemographicParameters()) -> np.ndarray:
    """Return survival probabilities for transitions from age x to age x+1."""

    survival = np.empty(params.maximum_age, dtype=float)
    survival[0] = params.calf_survival
    survival[1:60] = params.adult_survival
    ages = np.arange(60, params.maximum_age)
    survival[60:] = params.adult_survival * np.exp(
        -params.senescent_decay * (ages - 60)
    )
    return survival


def build_leslie_matrix(
    params: DemographicParameters = DemographicParameters(),
    treatment_fraction: float = 0.0,
) -> np.ndarray:
    """Construct an annual Leslie projection matrix."""

    matrix = np.zeros((params.age_classes, params.age_classes), dtype=float)
    matrix[0, :] = fertility_vector(params, treatment_fraction)
    matrix[np.arange(1, params.age_classes), np.arange(params.maximum_age)] = (
        survival_vector(params)
    )
    return matrix


def dominant_eigenvalue(matrix: np.ndarray) -> float:
    """Return the spectral radius, the asymptotic annual growth multiplier."""

    values = np.linalg.eigvals(matrix)
    return float(np.max(np.abs(values)))


def equilibrium_treatment_fraction(
    params: DemographicParameters = DemographicParameters(),
    tolerance: float = 1e-10,
) -> float:
    """Find the fertility reduction that makes the dominant eigenvalue one."""

    untreated = dominant_eigenvalue(build_leslie_matrix(params, 0.0))
    fully_treated = dominant_eigenvalue(build_leslie_matrix(params, 1.0))
    if not fully_treated <= 1.0 <= untreated:
        raise ValueError("The target eigenvalue is not bracketed by fractions 0 and 1")

    low, high = 0.0, 1.0
    while high - low > tolerance:
        middle = (low + high) / 2.0
        if dominant_eigenvalue(build_leslie_matrix(params, middle)) > 1.0:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def simulate(matrix: np.ndarray, initial_population: np.ndarray, years: int) -> np.ndarray:
    """Project an initial age distribution for a fixed number of years."""

    if years < 0:
        raise ValueError("years must be non-negative")
    initial = np.asarray(initial_population, dtype=float)
    if matrix.shape != (initial.size, initial.size):
        raise ValueError("matrix and population dimensions do not match")
    if np.any(initial < 0):
        raise ValueError("population counts cannot be negative")

    trajectory = np.empty((years + 1, initial.size), dtype=float)
    trajectory[0] = initial
    for year in range(years):
        trajectory[year + 1] = matrix @ trajectory[year]
    return trajectory


def synthetic_initial_population(
    total: float = 11_000.0,
    params: DemographicParameters = DemographicParameters(),
) -> np.ndarray:
    """Create a reproducible, data-free age profile for the public demonstration."""

    ages = np.arange(params.age_classes)
    profile = np.exp(-ages / 34.0) * (1.0 + 0.08 * np.cos(ages / 4.0))
    profile = np.maximum(profile, 0.0)
    return profile / profile.sum() * total
