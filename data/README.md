# Data provenance

The original class project referenced the 2000 COMAP Interdisciplinary Contest in
Modeling elephant-population problem and its accompanying spreadsheet:

- [ICM 2000 problem archive](https://www.contest.comap.com/undergraduate/contests/mcm/contests/2000/problems/icm.php)

No original spreadsheet, course document, or raw age-count table is redistributed in
this repository. The public example instead creates a deterministic synthetic age
profile, scaled to 11,000 animals, so the model can be run without copying the source
dataset. Replace `synthetic_initial_population()` with a vetted 71-element age vector
to study another population.
