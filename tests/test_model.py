import unittest

import numpy as np

from src.leslie_model import (
    build_leslie_matrix,
    dominant_eigenvalue,
    equilibrium_treatment_fraction,
    simulate,
    synthetic_initial_population,
)
from src.treatment_strategy import active_treatment_fraction, simulate_repeated_treatment


class LeslieModelTests(unittest.TestCase):
    def test_matrix_shape_and_nonnegative_entries(self):
        matrix = build_leslie_matrix()
        self.assertEqual(matrix.shape, (71, 71))
        self.assertTrue(np.all(matrix >= 0))

    def test_equilibrium_fraction_reproduces_reported_result(self):
        fraction = equilibrium_treatment_fraction()
        self.assertAlmostEqual(fraction, 0.2012, places=4)
        self.assertAlmostEqual(
            dominant_eigenvalue(build_leslie_matrix(treatment_fraction=fraction)),
            1.0,
            places=8,
        )

    def test_baseline_grows_asymptotically(self):
        self.assertGreater(dominant_eigenvalue(build_leslie_matrix()), 1.0)

    def test_simulation_dimensions_and_nonnegative_values(self):
        trajectory = simulate(build_leslie_matrix(), synthetic_initial_population(), 20)
        self.assertEqual(trajectory.shape, (21, 71))
        self.assertTrue(np.all(trajectory >= 0))

    def test_overlapping_treatment_events_compound(self):
        fraction = 0.2
        self.assertAlmostEqual(active_treatment_fraction(1, fraction, 2, 1), 0.36)
        self.assertAlmostEqual(active_treatment_fraction(2, fraction, 2, 2), 0.2)

    def test_scheduled_simulation_is_deterministic(self):
        initial = synthetic_initial_population()
        first, coverage = simulate_repeated_treatment(initial, 30, 0.2012, 2, 2)
        second, _ = simulate_repeated_treatment(initial, 30, 0.2012, 2, 2)
        np.testing.assert_allclose(first, second)
        self.assertTrue(np.all((coverage >= 0) & (coverage <= 1)))


if __name__ == "__main__":
    unittest.main()
